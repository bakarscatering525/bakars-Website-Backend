import httpx
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId

from app.config.database import get_database
from app.config.settings import settings
from app.models.order import OrderModel
from app.models.catering import CateringOrderModel
from app.services.auth_service import auth_service
from app.services.subscription_service import meal_subscription_service
from app.services.menu_service import menu_service
from app.services.email_service import (
    send_order_confirmation_email,
    send_email_async,
    EmailNotConfiguredError,
)
from app.utils.constants import OrderType

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self._db = None
        self._notifications_collection = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def notifications(self):
        if self._notifications_collection is None and self.db is not None:
            self._notifications_collection = self.db.notifications
        return self._notifications_collection

    async def _build_subscription_summary(self, order: OrderModel) -> str:
        """Compose a short summary of the meal subscription linked to the order."""
        if (
            not order.id
            or meal_subscription_service.subscriptions is None
        ):
            return ""

        try:
            subscription = await meal_subscription_service.subscriptions.find_one(
                {"order_id": ObjectId(order.id)}
            )
        except Exception as exc:
            logger.warning(
                "Unable to load subscription for order %s: %s",
                order.order_number,
                exc,
            )
            return ""

        if not subscription:
            return ""

        plan_lines = []
        for plan in subscription.get("plan_selections", []):
            plan_name = plan.get("plan_name") or plan.get("plan_code")
            quantity = plan.get("quantity", 1)
            included = plan.get("included_meals", 0)
            deliveries_in_cycle = plan.get("deliveries_in_cycle") or len(
                subscription.get("delivery_slots", [])
            )
            plan_lines.append(
                f"  • {plan_name} x{quantity} ({included} meals, {deliveries_in_cycle} deliveries)"
            )
            delivery_days = plan.get("available_delivery_days") or []
            if delivery_days:
                plan_lines.append(
                    f"     Days: {', '.join(day.title() for day in delivery_days)}"
                )

        delivery_lines = []
        for slot in subscription.get("delivery_slots", []):
            raw_date = slot.get("delivery_date")
            if hasattr(raw_date, "strftime"):
                date_str = raw_date.strftime("%d %b")
            else:
                date_str = str(raw_date)
            total_boxes = sum((slot.get("menu_items") or {}).values())
            delivery_lines.append(f"  • {date_str}: {total_boxes} box(es)")

        reminder_line = ""
        reminder_settings = subscription.get("reminder_settings")
        if reminder_settings and reminder_settings.get("enabled"):
            frequency = reminder_settings.get("frequency_days", 7)
            channel = reminder_settings.get("channel", "in_app").replace("_", " ").title()
            reminder_line = f"Reminders: every {frequency} day(s) via {channel}"

        sections = []
        if plan_lines:
            sections.append("*Plan Details:*\n" + "\n".join(plan_lines))
        if delivery_lines:
            sections.append("*Scheduled Deliveries:*\n" + "\n".join(delivery_lines))
        if reminder_line:
            sections.append(reminder_line)

        return "\n".join(sections)

    async def send_in_app_notification(
        self,
        *,
        user_id: str | ObjectId,
        title: str,
        message: str,
        notification_type: str = "reminder",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Persist an in-app notification for the user."""
        collection = self.notifications
        if collection is None:
            logger.warning("Notifications collection unavailable; cannot store in-app notification.")
            return False

        try:
            user_object_id = user_id if isinstance(user_id, ObjectId) else ObjectId(str(user_id))
        except Exception as exc:
            logger.error("Invalid user_id for in-app notification (%s): %s", user_id, exc)
            return False

        document = {
            "user_id": user_object_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "channel": "in_app",
            "metadata": metadata or {},
            "read": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        try:
            await collection.insert_one(document)
            return True
        except Exception as exc:
            logger.error("Failed to persist in-app notification: %s", exc, exc_info=True)
            return False

    async def send_email_notification(
        self,
        email: Optional[str],
        *,
        subject: str,
        message: str,
    ) -> bool:
        """Send a simple transactional email."""
        if not email:
            logger.warning("Missing recipient email; skipping reminder email notification.")
            return False

        try:
            await send_email_async(
                subject=subject,
                body_text=message,
                body_html=None,
                recipients=[email],
            )
            return True
        except EmailNotConfiguredError:
            logger.warning("Email service not configured; cannot send reminder email.")
            return False
        except Exception as exc:
            logger.error("Failed to send reminder email: %s", exc, exc_info=True)
            return False
    
    async def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message via Business API"""
        try:
            # Clean phone number
            phone = phone_number.replace(" ", "").replace("-", "")
            if phone.startswith("0"):
                phone = "+61" + phone[1:]
            elif not phone.startswith("+"):
                phone = "+61" + phone
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"WhatsApp message sent to {phone}")
                    return True
                else:
                    logger.error(f"Failed to send WhatsApp message: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_order_confirmation(self, order: OrderModel) -> bool:
        """Send order confirmation notification"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False

            subscription_details = None
            if (
                order.order_type == OrderType.MEAL_SUBSCRIPTION.value
                and meal_subscription_service.subscriptions is not None
            ):
                try:
                    subscription_doc = await meal_subscription_service.subscriptions.find_one(
                        {"order_id": ObjectId(order.id)}
                    )
                    if subscription_doc:
                        # Build slot items with menu metadata
                        delivery_slots = []
                        all_menu_ids = set()
                        for slot in subscription_doc.get("delivery_slots", []):
                            for key in (slot.get("menu_items") or {}).keys():
                                try:
                                    all_menu_ids.add(str(key))
                                except Exception:
                                    continue
                        menu_lookup: Dict[str, Any] = {}
                        if all_menu_ids:
                            try:
                                menu_items = await menu_service.get_menu_items_by_ids(list(all_menu_ids))
                                for item in menu_items:
                                    if not item or getattr(item, "id", None) is None:
                                        continue
                                    menu_lookup[str(item.id)] = {
                                        "name": getattr(item, "name", None),
                                        "category": getattr(item, "category", None),
                                        "price": getattr(item, "price", None),
                                    }
                            except Exception as slot_lookup_error:
                                logger.warning("Failed to load menu items for delivery slots: %s", slot_lookup_error)
                        for slot in subscription_doc.get("delivery_slots", []):
                            raw_date = slot.get("delivery_date")
                            delivery_date = raw_date.strftime("%Y-%m-%d") if hasattr(raw_date, "strftime") else str(raw_date)
                            items = []
                            for menu_id, qty in (slot.get("menu_items") or {}).items():
                                meta = menu_lookup.get(str(menu_id)) or {}
                                items.append(
                                    {
                                        "menu_item_id": str(menu_id),
                                        "name": meta.get("name") or "Meal",
                                        "category": meta.get("category"),
                                        "quantity": qty,
                                        "price": meta.get("price"),
                                        "subtotal": (meta.get("price") or 0) * (qty or 1),
                                    }
                                )
                            delivery_slots.append(
                                {
                                    "delivery_date": delivery_date,
                                    "items": items,
                                    "notes": slot.get("notes"),
                                }
                            )
                        subscription_details = {
                            "plan_selections": subscription_doc.get("plan_selections", []),
                            "delivery_slots": delivery_slots,
                            "fulfilment": subscription_doc.get("fulfilment_type"),
                        }
                except Exception as sub_error:
                    logger.warning("Unable to attach subscription details for email: %s", sub_error)

            item_lines = [
                f"- {item.item_name} x{item.quantity} - ${item.subtotal:.2f}"
                for item in order.items
            ]

            delivery_lines = []
            if order.delivery_method != "pickup" and order.delivery_address:
                addr = order.delivery_address
                street = addr.get("street") if isinstance(addr, dict) else getattr(addr, "street", "")
                suburb = addr.get("suburb") if isinstance(addr, dict) else getattr(addr, "suburb", "")
                postcode = addr.get("postcode") if isinstance(addr, dict) else getattr(addr, "postcode", "")
                if street:
                    delivery_lines.append(street)
                city_line = " ".join(value for value in [suburb, postcode] if value)
                if city_line:
                    delivery_lines.append(city_line.strip())

            subscription_summary = ""
            if order.order_type == OrderType.MEAL_SUBSCRIPTION.value:
                subscription_summary = await self._build_subscription_summary(order)

            message_lines = [
                "*Order Confirmed!*",
                "",
                "Thank you for your order at Bakar's Food & Catering!",
                "",
                "*Order Details:*",
                f"Order Number: {order.order_number}",
                f"Order Type: {order.order_type.title()}",
            ]

            if item_lines:
                message_lines.extend(["", "*Items:*", *item_lines])

            message_lines.extend(
                [
                    "",
                    "*Payment Summary:*",
                    f"Subtotal: ${order.subtotal:.2f}",
                    f"Delivery Fee: ${order.delivery_fee:.2f}",
                    f"Total: ${order.total_amount:.2f}",
                ]
            )

            if delivery_lines:
                message_lines.extend(["", "Delivery Address:", *delivery_lines])

            if subscription_summary:
                message_lines.extend(["", subscription_summary])

            message_lines.extend(
                [
                    "",
                    f"Status: {order.status.title()}",
                    "",
                    "We'll notify you when your order is ready!",
                    "",
                    "For any queries, contact us:",
                    "Phone: [Your Phone Number]",
                    "Email: [Your Email]",
                    "",
                    "Thank you for choosing Bakar's Food & Catering!",
                ]
            )

            message = "\n".join(message_lines)

            email_sent = False
            customer_name = " ".join(filter(None, [getattr(user, "first_name", ""), getattr(user, "last_name", "")])).strip()
            customer_email = getattr(user, "email", None)
            customer_phone = getattr(user, "phone", None)

            if customer_email:
                try:
                    await send_order_confirmation_email(
                        order=order,
                        customer_email=customer_email,
                        customer_name=customer_name or customer_email.split("@")[0],
                        restaurant_email=settings.ORDER_NOTIFICATIONS_EMAIL,
                        customer_phone=customer_phone,
                        subscription=subscription_details,
                    )
                    email_sent = True
                except Exception as email_error:
                    logger.error("Failed to send order confirmation email: %s", email_error)

            whatsapp_sent = False
            whatsapp_configured = all([self.api_url, self.access_token, self.phone_number_id])
            if whatsapp_configured and getattr(user, "phone", None):
                whatsapp_sent = await self.send_whatsapp_message(user.phone, message)

            return whatsapp_sent or email_sent

        except Exception as e:
            logger.error(f"Error sending order confirmation: {e}")
            return False


    async def send_meal_plan_update_notifications(self, order: OrderModel) -> bool:
        """Notify customer and admin when a meal subscription is updated."""
        if not order or order.order_type != OrderType.MEAL_SUBSCRIPTION.value:
            return False

        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
        except Exception as exc:
            logger.error("Unable to load user for meal plan update: %s", exc)
            user = None

        plan_label = order.primary_plan_name or order.primary_plan_tab or "meal plan"
        summary = await self._build_subscription_summary(order)
        order_number = order.order_number or str(order.id)
        timestamp = datetime.utcnow().strftime("%d %b %Y at %I:%M %p")

        email_tasks = []
        customer_email = getattr(user, "email", None)
        customer_name = " ".join(
            filter(None, [getattr(user, "first_name", ""), getattr(user, "last_name", "")])
        ).strip()

        if customer_email:
            customer_subject = f"Meal plan updated - Order {order_number}"
            customer_lines = [
                f"Hi {customer_name or 'there'},",
                "",
                f"Your {plan_label} has been updated on {timestamp}.",
                "You can review the latest schedule inside your account.",
            ]
            if summary:
                customer_lines.extend(["", summary])
            customer_lines.extend(
                [
                    "",
                    "If you did not request these changes, please contact our support team.",
                    "",
                    "Thank you,",
                    "Bakar's Food & Catering",
                ]
            )
            try:
                await send_email_async(
                    subject=customer_subject,
                    body_text="\n".join(customer_lines),
                    body_html=None,
                    recipients=[customer_email],
                )
                email_tasks.append(True)
            except Exception as exc:
                logger.error("Failed to send meal plan update email to customer: %s", exc)

        admin_email = getattr(settings, "ORDER_NOTIFICATIONS_EMAIL", None)
        if admin_email:
            admin_subject = f"Meal subscription updated - Order {order_number}"
            admin_lines = [
                "Hello team,",
                "",
                f"The meal subscription for {customer_name or customer_email or order.user_id} was updated.",
                f"Plan: {plan_label}",
                f"Timestamp: {timestamp}",
            ]
            if summary:
                admin_lines.extend(["", summary])
            admin_lines.extend(
                [
                    "",
                    "This is an automated notification.",
                ]
            )
            try:
                await send_email_async(
                    subject=admin_subject,
                    body_text="\n".join(admin_lines),
                    body_html=None,
                    recipients=[admin_email],
                )
                email_tasks.append(True)
            except Exception as exc:
                logger.error("Failed to send meal plan update email to admin: %s", exc)

        if user:
            try:
                await self.send_in_app_notification(
                    user_id=str(order.user_id),
                    title="Meal plan updated",
                    message=f"Your {plan_label} was updated on {timestamp}.",
                    notification_type="meal_plan_update",
                    metadata={"order_id": str(order.id), "order_number": order_number},
                )
            except Exception as exc:
                logger.warning("Failed to create in-app notification for meal plan update: %s", exc)

        return any(email_tasks)

    async def send_catering_quote(self, order: OrderModel, catering: CateringOrderModel) -> bool:
        """Send catering quote via WhatsApp"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False
            
            event_date = catering.event_date.strftime("%d %B %Y")

            message_lines = [
                "📋 *Catering Quote*",
                "",
                "Thank you for choosing Bakar's Food & Catering!",
                "",
                f"*Order Number:* {order.order_number}",
                "",
                "*Event Details:*",
                f"Date: {event_date}",
                f"Time: {catering.event_time or 'TBD'}",
                f"Venue: {catering.venue_address}",
                f"Guest Count: {catering.guest_count}",
                "",
                "*Package Selected:*",
                f"{catering.package_type.title()} Package",
                f"Price: ${catering.package_price_per_head}/head",
                "",
                "*Pricing Breakdown:*",
                f"Package Total: ${catering.package_total:.2f}",
                f"Delivery Fee: ${catering.delivery_fee:.2f}",
                f"Total Amount: ${order.total_amount:.2f}",
                "",
                "*Payment Terms:*",
                f"Advance Payment (50%): ${catering.advance_payment_amount:.2f}",
                f"Balance Payment: ${catering.remaining_payment_amount:.2f}",
                "",
                "Special Requests:",
                catering.special_requests or "None",
                "",
                "Please confirm your booking by paying the advance amount.",
                "",
                "For any changes or queries, contact us:",
                "📞 [Your Phone Number]",
                "📧 [Your Email]",
                "",
                "We look forward to catering your event! 🎊",
            ]

            message = "\n".join(message_lines)

            return await self.send_whatsapp_message(user.phone, message)
            
        except Exception as e:
            logger.error(f"Error sending catering quote: {e}")
            return False
    
    async def send_status_update(self, order: OrderModel, new_status: str) -> bool:
        """Send order status update"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False
            
            status_messages = {
                "confirmed": "Your order has been confirmed and is being prepared! 👨‍🍳",
                "preparing": "Your order is being prepared with love! 🔥",
                "out_for_delivery": "Your order is on the way! 🚗",
                "delivered": "Your order has been delivered! Enjoy your meal! 😋",
                "cancelled": "Your order has been cancelled. Contact us for details. ℹ️",
            }

            message_lines = [
                "*Order Status Update*",
                "",
                f"Order Number: {order.order_number}",
                "",
                f"Status: {new_status.title().replace('_', ' ')}",
            ]

            status_note = status_messages.get(new_status)
            if status_note:
                message_lines.append(status_note)

            message_lines.extend(
                [
                    "",
                    "Track your order: [Your tracking URL]",
                    "",
                    "Thank you for choosing Bakar's Food & Catering! 🍛",
                ]
            )

            message = "\n".join(message_lines)

            return await self.send_whatsapp_message(user.phone, message)
            
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
            return False

notification_service = NotificationService()
