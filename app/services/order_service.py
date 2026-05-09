from typing import List, Optional, Dict, Any, Tuple, Set
from bson import ObjectId
from datetime import datetime, timedelta, time, timezone
from collections import defaultdict, Counter
from app.config.database import get_database
from app.models.order import OrderModel, OrderItem
from app.models.subscription import MealSubscriptionModel, MealPlanSelection, DeliverySlotSelection
from app.models.catering import CateringOrderModel
from app.utils.helpers import generate_order_number, parse_date
from app.utils.constants import (
    OrderType, OrderStatus, PaymentStatus,
    DAILY_DELIVERY_FEE,
    REGULAR_DELIVERY_MIN_BOXES,
    REGULAR_PICKUP_MIN_BOXES,
    DEFAULT_EXTRA_BOX_PRICE,
    CATERING_BASIC_PRICE, CATERING_PREMIUM_PRICE, CATERING_DIAMOND_PRICE,
    CATERING_ADVANCE_PAYMENT_PERCENT, CATERING_BASE_DELIVERY_FEE
)
from app.services.menu_service import menu_service
from app.services.delivery_service import delivery_service
from app.services.subscription_service import meal_subscription_service
from app.services.reminder_service import reminder_service
from app.services.notification_service import notification_service
from app.utils.time_windows import require_daily_menu_open, get_business_now, get_business_timezone
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self._db = None
        self._orders = None
        self._meal_subs = None
        self._legacy_weekly_subs = None
        self._catering_orders = None
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def orders(self):
        """Get orders collection lazily"""
        if self._orders is None and self.db is not None:
            self._orders = self.db.orders
        return self._orders
    
    @property
    def meal_subs(self):
        """Get meal_subscriptions collection lazily"""
        if self._meal_subs is None and self.db is not None:
            self._meal_subs = self.db.meal_subscriptions
        return self._meal_subs
    
    @property
    def weekly_subs_legacy(self):
        """Access legacy weekly subscription collection if still present."""
        if self._legacy_weekly_subs is None and self.db is not None:
            self._legacy_weekly_subs = getattr(self.db, "weekly_subscriptions", None)
        return self._legacy_weekly_subs
    
    @property
    def catering_orders(self):
        """Get catering_orders collection lazily"""
        if self._catering_orders is None and self.db is not None:
            self._catering_orders = self.db.catering_orders
        return self._catering_orders
    
    async def create_daily_order(
        self,
        user_id: str,
        items: List[Dict],
        delivery_method: str,
        delivery_address: dict,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
    ) -> OrderModel:
        """Create daily menu order"""
        try:
            if self.orders is None or self.db is None:
                raise ValueError("Database not connected")

            # Enforce ordering window for daily menu
            require_daily_menu_open()
                
            # Calculate order items
            order_items = []
            subtotal = 0.0
            
            normalized_items = [
                item_data.dict() if hasattr(item_data, "dict") else item_data
                for item_data in items
            ]

            for item_data in normalized_items:
                item_id = item_data.get("item_id")
                quantity = item_data.get("quantity")

                if not item_id or not quantity:
                    raise ValueError("Invalid daily order items payload")
                
                menu_item = await menu_service.get_menu_item_by_id(item_id)
                if not menu_item or not menu_item.is_available_for_daily:
                    raise ValueError(f"Item {item_id} not available for daily orders")
                
                order_item = OrderItem(
                    item_id=str(menu_item.id),
                    item_name=menu_item.name,
                    category=menu_item.category,
                    quantity=quantity,
                    price=menu_item.price,
                    subtotal=menu_item.price * quantity
                )
                order_items.append(order_item)
                subtotal += order_item.subtotal
            
            # Calculate delivery fee
            delivery_fee = 0.0
            if delivery_method == "standard":
                # Check delivery availability
                address_str = f"{delivery_address['street']}, {delivery_address['suburb']}, {delivery_address['postcode']}"
                is_available, distance, geocoded, failure_reason, computed_fee = await delivery_service.check_daily_delivery(address_str)
                
                if not is_available:
                    message = failure_reason or "Daily delivery is restricted to addresses within 6km of Guildford."
                    logger.warning(f"Daily order blocked for address '{address_str}': {message}")
                    raise ValueError(message)
                
                delivery_fee = computed_fee if computed_fee is not None else DAILY_DELIVERY_FEE
                if geocoded:
                    delivery_address["latitude"] = geocoded.get("latitude")
                    delivery_address["longitude"] = geocoded.get("longitude")
                    if geocoded.get("formatted_address"):
                        delivery_address["formatted_address"] = geocoded["formatted_address"]
            
            total_amount = subtotal + delivery_fee
            
            # Create order document for MongoDB
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),  # Store as ObjectId in MongoDB
                "order_type": OrderType.DAILY,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "payment_method": (payment_method or "cash").lower(),
                "items": [item.dict() for item in order_items],
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "total_amount": total_amount,
                "delivery_method": delivery_method,
                "delivery_address": delivery_address,
                "delivery_instructions": delivery_instructions,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id

            # Convert all ObjectIds to strings for the response model
            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),  # Convert ObjectId to string
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "subtotal": order_dict["subtotal"],
                "tax_amount": order_dict.get("tax_amount", 0.0),
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "delivery_instructions": order_dict["delivery_instructions"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"]
            }

            logger.info(f"Daily order created: {order_dict['order_number']}")
            return OrderModel(**response_dict)
            
        except Exception as e:
            logger.error(f"Error creating daily order: {e}")
            raise

    async def _prepare_meal_subscription_documents(
        self,
        user_id: str,
        plan_selections: List[Dict[str, Any]],
        delivery_slots: List[Dict[str, Any]],
        sidelines: Optional[List[Dict[str, Any]]],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: Optional[str],
        notes: Optional[str],
        payment_method: str,
        delivery_address_id: Optional[str],
        existing_subscription: Optional[Dict[str, Any]] = None,
        cutoff_override_dates: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], int]:
        """Shared preparation logic for creating/updating meal subscription orders."""
        if not plan_selections:
            raise ValueError("At least one plan selection is required")

        if not delivery_slots:
            raise ValueError("Delivery schedule is required")

        fulfilment = (fulfilment_method or "delivery").lower()
        address_data = dict(delivery_address or {})

        plan_records: List[Dict[str, Any]] = []
        total_included_boxes = 0
        plan_base_total = 0.0
        has_regular_plan = False
        has_subscription_plan = False
        now = get_business_now()
        business_tz = get_business_timezone()
        now_local = now.astimezone(business_tz)

        existing_slots_by_date: Dict[str, Dict[str, Any]] = {}
        if existing_subscription:
            for slot in existing_subscription.get("delivery_slots", []):
                raw_date = slot.get("delivery_date")
                date_key = (
                    raw_date.strftime("%Y-%m-%d")
                    if isinstance(raw_date, datetime)
                    else str(raw_date)
                )
                menu_items_existing: Dict[str, int] = {}
                for key, qty in (slot.get("menu_items") or {}).items():
                    try:
                        int_qty = int(qty)
                    except (TypeError, ValueError):
                        continue
                    if int_qty <= 0:
                        continue
                    menu_items_existing[str(key)] = int_qty

                existing_slots_by_date[date_key] = {
                    "menu_items": menu_items_existing,
                    "locked_at": slot.get("locked_at"),
                }

        for selection in plan_selections:
            plan_id = selection.get("plan_id")
            quantity = int(selection.get("quantity", 1))
            if quantity <= 0:
                raise ValueError("Plan quantity must be at least 1")

            plan = await meal_subscription_service.get_plan_by_id(plan_id)
            if not plan or not plan.is_active:
                raise ValueError("Selected meal subscription plan is not available")

            if not plan.allow_multiple and quantity > 1:
                raise ValueError(f"{plan.name} cannot be selected more than once")

            included_boxes = (plan.included_meals or 0) * quantity
            plan_price = (plan.price_per_plan or 0.0) * quantity

            total_included_boxes += included_boxes
            plan_base_total += plan_price
            has_regular_plan = has_regular_plan or plan.tab == "regular"
            has_subscription_plan = has_subscription_plan or (plan.included_meals or 0) > 0

            plan_records.append(
                {
                    "plan": plan,
                    "quantity": quantity,
                    "included_boxes": included_boxes,
                    "plan_price": plan_price,
                }
            )

        unique_plan_tabs = {record["plan"].tab for record in plan_records}
        if len(unique_plan_tabs) > 1:
            raise ValueError("Please select one meal plan type per order.")

        primary_plan = plan_records[0]["plan"]
        primary_plan_tab = getattr(primary_plan, "tab", None)
        primary_plan_name = getattr(primary_plan, "name", None)
        plan_week_rules = getattr(primary_plan, "week_selection_rules", None)

        delivery_slot_models: List[DeliverySlotSelection] = []
        menu_totals: Dict[str, int] = defaultdict(int)
        unique_delivery_dates = set()
        unique_delivery_dates_delivery = set()

        for slot in delivery_slots:
            date_str = slot.get("delivery_date")
            menu_items = slot.get("menu_items", {})
            if not date_str or not menu_items:
                continue

            slot_fulfilment = (slot.get("fulfilment_method") or fulfilment).lower()
            if slot_fulfilment not in {"delivery", "pickup"}:
                slot_fulfilment = fulfilment

            raw_variation_sizes = slot.get("variation_sizes") or {}
            slot_variation_sizes: Dict[str, str] = {}
            if isinstance(raw_variation_sizes, dict):
                for raw_id, raw_size in raw_variation_sizes.items():
                    if raw_id is None or raw_size is None:
                        continue
                    item_id = str(raw_id).strip()
                    size = str(raw_size).strip().lower()
                    if not item_id or not size:
                        continue
                    slot_variation_sizes[item_id] = size

            delivery_date = parse_date(date_str)
            date_key = delivery_date.date().isoformat()

            # Normalize menu items (string IDs, positive integers)
            normalized_menu_items: Dict[str, int] = {}
            for item_id, quantity in menu_items.items():
                str_id = str(item_id).strip()
                try:
                    qty = int(quantity)
                except (TypeError, ValueError):
                    qty = 0
                if not str_id or qty <= 0:
                    continue
                normalized_menu_items[str_id] = qty

            if not normalized_menu_items:
                raise ValueError(f"Please assign meals for {date_key}")

            # Enforce meal subscription daily cutoff in business timezone (default Australia/Sydney):
            # orders for a given delivery date close at 12:05 AM of that date.
            delivery_date_local = datetime.combine(
                delivery_date.date(),
                time(hour=0, minute=5),
                tzinfo=business_tz,
            )
            cutoff_at_utc = delivery_date_local.astimezone(timezone.utc)

            existing_slot = existing_slots_by_date.get(date_key)
            existing_items = existing_slot.get("menu_items") if existing_slot else None
            is_changed = (
                existing_items is None or normalized_menu_items != existing_items
            )
            is_override = cutoff_override_dates is not None and date_key in cutoff_override_dates
            is_past_cutoff = now_local >= delivery_date_local

            if is_past_cutoff and not is_override and is_changed:
                raise ValueError(
                    f"Ordering for {delivery_date.date().isoformat()} closed at 12:05 AM. "
                    "Please contact support to modify this delivery."
                )

            lock_timestamp = existing_slot.get("locked_at") if existing_slot else None
            if is_past_cutoff and lock_timestamp is None and not is_override:
                lock_timestamp = cutoff_at_utc

            delivery_slot_models.append(
                DeliverySlotSelection(
                    delivery_date=delivery_date,
                    menu_items=normalized_menu_items,
                    variation_sizes=slot_variation_sizes,
                    fulfilment_method=slot_fulfilment,
                    notes=slot.get("notes"),
                    cutoff_at=cutoff_at_utc,
                    locked_at=lock_timestamp,
                )
            )

            unique_delivery_dates.add(date_str)
            if slot_fulfilment == "delivery":
                unique_delivery_dates_delivery.add(date_str)

            for item_id, quantity in normalized_menu_items.items():
                menu_totals[item_id] += int(quantity)

        if not delivery_slot_models:
            raise ValueError("No meals were selected for the delivery schedule")

        total_selected_boxes = sum(menu_totals.values())
        week_counts: Counter[str] = Counter()
        for slot in delivery_slot_models:
            delivery_date = slot.delivery_date
            week_start = delivery_date.date() - timedelta(days=delivery_date.weekday())
            week_counts[week_start.isoformat()] += 1

        if plan_week_rules and primary_plan.tab != "regular":
            # Allow customers to concentrate all meals into any preferred week/day,
            # but still honor the maximum selectable weeks defined by the plan.
            available_weeks = plan_week_rules.available_weeks
            unique_week_count = len(week_counts)

            if available_weeks and unique_week_count > available_weeks:
                raise ValueError(
                    f"{primary_plan.name} allows choosing from only "
                    f"{available_weeks} upcoming week(s)."
                )

        allow_partial_selection = primary_plan.tab != "regular"
        if has_subscription_plan and total_selected_boxes < total_included_boxes:
            missing = total_included_boxes - total_selected_boxes
            if not allow_partial_selection:
                raise ValueError(f"Please select {missing} more meal(s) to complete your plan")
            # Allow non-regular plans to proceed with unassigned boxes; reminders handle the gap.
            logger.info(
                "Proceeding with %d unassigned meal(s) for plan %s",
                missing,
                getattr(primary_plan, "code", None) or getattr(primary_plan, "name", None),
            )

        if fulfilment == "delivery" and has_regular_plan and total_selected_boxes < REGULAR_DELIVERY_MIN_BOXES:
            raise ValueError(f"Regular delivery orders require at least {REGULAR_DELIVERY_MIN_BOXES} boxes")

        if fulfilment == "pickup" and has_regular_plan and total_selected_boxes < REGULAR_PICKUP_MIN_BOXES:
            raise ValueError(f"Regular pickup orders require at least {REGULAR_PICKUP_MIN_BOXES} box")

        # Cache menu items to avoid repeated lookups
        menu_item_cache: Dict[str, Any] = {}

        async def get_menu_item_cached(item_id: str):
            if item_id in menu_item_cache:
                return menu_item_cache[item_id]
            menu_item = await menu_service.get_menu_item_by_id(item_id)
            menu_item_cache[item_id] = menu_item
            return menu_item

        add_on_total = 0.0

        def resolve_unit_price(menu_item: Any, variation_size: Optional[str]) -> float:
            base = float(getattr(menu_item, "price", 0.0) or 0.0)
            if not variation_size:
                return base
            size = str(variation_size).strip().lower()
            variations = getattr(menu_item, "variations", None) or []
            for variation in variations:
                try:
                    v_size = str(variation.get("size", "")).strip().lower()
                except Exception:
                    v_size = ""
                if v_size != size:
                    continue
                try:
                    is_available = bool(variation.get("is_available", True))
                except Exception:
                    is_available = True
                if not is_available:
                    continue
                try:
                    return float(variation.get("price", base) or base)
                except Exception:
                    return base
            return base

        # Build priced order items (group by item + variation size) and compute subtotal.
        item_totals: Dict[tuple[str, Optional[str]], Dict[str, Any]] = defaultdict(
            lambda: {"quantity": 0, "unit_price": 0.0, "name": "", "category": ""}
        )
        meals_subtotal = 0.0

        for slot in delivery_slot_models:
            for item_id, quantity in slot.menu_items.items():
                menu_item = await get_menu_item_cached(item_id)
                if not menu_item or not getattr(menu_item, "is_available", True):
                    raise ValueError(f"Menu item {item_id} is no longer available")
                if has_subscription_plan and not getattr(menu_item, "is_available_for_meal_plan", False):
                    raise ValueError(f"{getattr(menu_item, 'name', item_id)} is not available for meal subscriptions")

                qty = int(quantity)
                if qty <= 0:
                    continue

                variation_size = (slot.variation_sizes or {}).get(item_id)
                unit_price = resolve_unit_price(menu_item, variation_size)
                meals_subtotal += unit_price * qty

                key = (str(menu_item.id), variation_size)
                item_totals[key]["quantity"] += qty
                item_totals[key]["unit_price"] = unit_price
                item_totals[key]["name"] = getattr(menu_item, "name", "Item")
                item_totals[key]["category"] = getattr(menu_item, "category", "")

        order_items: List[OrderItem] = []
        for (resolved_id, variation_size), payload in item_totals.items():
            label = payload["name"]
            if variation_size:
                label = f"{label} ({variation_size})"
            quantity = int(payload["quantity"])
            unit_price = float(payload["unit_price"])
            order_items.append(
                OrderItem(
                    item_id=resolved_id,
                    item_name=label,
                    category=str(payload["category"]),
                    quantity=quantity,
                    price=unit_price,
                    subtotal=unit_price * quantity,
                )
            )

        # Process add-ons / sidelines if provided
        sideline_items: List[OrderItem] = []
        if sidelines:
            for entry in sidelines:
                if hasattr(entry, "model_dump"):
                    entry_dict = entry.model_dump()
                elif hasattr(entry, "dict"):
                    entry_dict = entry.dict()
                elif isinstance(entry, dict):
                    entry_dict = entry
                else:
                    logger.warning("Skipping unrecognized sideline payload: %s", entry)
                    continue

                sideline_id = str(entry_dict.get("item_id") or "").strip()
                sideline_qty_raw = entry_dict.get("quantity", 0)
                try:
                    sideline_qty = int(sideline_qty_raw)
                except (TypeError, ValueError):
                    sideline_qty = 0
                if not sideline_id or sideline_qty <= 0:
                    continue

                menu_item = await menu_service.get_menu_item_by_id(sideline_id)
                if not menu_item or not menu_item.is_available:
                    raise ValueError(f"Add-on item {sideline_id} is no longer available")

                sideline_subtotal = sideline_qty * menu_item.price
                sideline_items.append(
                    OrderItem(
                        item_id=str(menu_item.id),
                        item_name=menu_item.name,
                        category=menu_item.category,
                        quantity=sideline_qty,
                        price=menu_item.price,
                        subtotal=sideline_subtotal,
                    )
                )
                add_on_total += sideline_subtotal

        # Deal discount rules (updated):
        # - Weekly: flat $20 off, any quantity.
        # - Fortnight: flat $50 off, requires 20+ meals selected.
        discount_amount = 0.0
        if primary_plan_tab == "weekly" and total_selected_boxes > 0:
            discount_amount = 20.0
        elif primary_plan_tab == "fortnight":
            if total_selected_boxes < 20:
                raise ValueError("Please select at least 20 meals to unlock the $50 deal.")
            discount_amount = 50.0

        subtotal = meals_subtotal + add_on_total
        subtotal_after_discount = max(0.0, subtotal - discount_amount)
        tax_amount = round(subtotal_after_discount * 0.10, 2)

        delivery_days = len(unique_delivery_dates_delivery)
        delivery_fee = 0.0
        delivery_fee_per_day = 0.0
        has_any_delivery = delivery_days > 0

        if has_any_delivery:
            address_required_fields = ["street", "suburb", "postcode"]
            if any(field not in address_data for field in address_required_fields):
                raise ValueError("Delivery address is incomplete")

            address_str = f"{address_data['street']}, {address_data['suburb']}, {address_data['postcode']}"
            delivery_fee, distance, geocoded = await delivery_service.calculate_weekly_delivery_fee(
                address_str,
                subtotal_after_discount,
                max(delivery_days, 1),
                is_express
            )

            if geocoded:
                address_data["latitude"] = geocoded["latitude"]
                address_data["longitude"] = geocoded["longitude"]
                address_data["formatted_address"] = geocoded.get("formatted_address")

            delivery_fee_per_day = delivery_fee / max(delivery_days, 1)
        else:
            address_data = {"fulfilment": "pickup"}
            delivery_address_id = None

        total_amount = subtotal_after_discount + tax_amount + delivery_fee

        plan_selection_models = []
        for record in plan_records:
            plan_obj = record["plan"]
            quantity = record["quantity"]
            weeks_in_cycle = plan_obj.weeks_in_cycle or (
                plan_obj.week_selection_rules.available_weeks
                if plan_obj.week_selection_rules and plan_obj.week_selection_rules.available_weeks
                else 0
            )
            selection = MealPlanSelection(
                plan_id=str(plan_obj.id),
                plan_code=plan_obj.code,
                plan_name=plan_obj.name,
                plan_tab=plan_obj.tab,
                quantity=quantity,
                included_meals=(plan_obj.included_meals or 0) * quantity,
                included_boxes=record["included_boxes"],
                deliveries_in_cycle=plan_obj.deliveries_per_cycle or delivery_days,
                weeks_in_cycle=weeks_in_cycle,
                max_boxes_per_meal=plan_obj.max_boxes_per_meal,
                available_delivery_days=plan_obj.available_delivery_days or [],
                week_selection_rules=plan_obj.week_selection_rules,
                customer_notifications=plan_obj.customer_notifications,
                metadata=plan_obj.metadata,
                plan_price=record["plan_price"],
                discount_applied=0.0,
            )
            plan_selection_models.append(selection)

        order_payload = {
            "items": [item.dict() for item in order_items],
            "sidelines": [item.dict() for item in sideline_items],
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "delivery_fee": delivery_fee,
            "total_amount": total_amount,
            "plan_price_total": 0.0,
            "delivery_method": (
                "pickup"
                if not has_any_delivery
                else ("express" if is_express else "standard")
            ),
            "delivery_address": address_data,
            "delivery_address_id": delivery_address_id,
            "delivery_instructions": delivery_instructions,
            "notes": notes,
            "payment_method": (payment_method or "cash").lower(),
            "primary_plan_tab": primary_plan_tab,
            "primary_plan_name": primary_plan_name,
            "extra_boxes": 0,
            "extra_boxes_price": 0.0,
        }

        subscription_payload = {
            "user_id": ObjectId(user_id),
            "fulfilment_type": (
                "mixed"
                if has_any_delivery and len(unique_delivery_dates) > len(unique_delivery_dates_delivery)
                else ("delivery" if has_any_delivery else "pickup")
            ),
            "postal_code": address_data.get("postcode") if has_any_delivery else None,
            "plan_selections": [selection.dict() for selection in plan_selection_models],
            "delivery_slots": [slot.dict() for slot in delivery_slot_models],
            "total_selected_boxes": total_selected_boxes,
            "total_included_boxes": total_included_boxes,
            "extra_boxes": 0,
            "extra_boxes_price": 0.0,
            "tax_amount": tax_amount,
            "plan_price_total": 0.0,
            "delivery_days": delivery_days,
            "delivery_fee_per_day": delivery_fee_per_day,
            "total_delivery_fee": delivery_fee,
            "express_delivery": has_any_delivery and is_express,
            "delivery_fee_notes": None,
            "reminder_settings": (
                primary_plan.reminder_settings.dict()
                if getattr(primary_plan, "reminder_settings", None)
                else None
            ),
            "reminders_sent": [],
            "is_active": True,
        }

        remaining_unfilled = max(total_included_boxes - total_selected_boxes, 0)
        return order_payload, subscription_payload, plan_records, remaining_unfilled

    async def create_meal_subscription_order(
        self,
        user_id: str,
        plan_selections: List[Dict],
        delivery_slots: List[Dict],
        sidelines: Optional[List[Dict]],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
        delivery_address_id: Optional[str] = None,
    ) -> tuple[OrderModel, MealSubscriptionModel]:
        """Create a configurable meal subscription (weekly/fortnight/monthly/regular) order."""
        try:
            if self.orders is None or self.db is None:
                raise ValueError("Database not connected")

            subscription_collection = (
                self.meal_subs
                if self.meal_subs is not None
                else self.weekly_subs_legacy
            )
            if subscription_collection is None:
                raise ValueError("Meal subscription collection not available")

            (
                order_payload,
                subscription_payload,
                plan_records,
                remaining_unfilled,
            ) = await self._prepare_meal_subscription_documents(
                user_id,
                plan_selections,
                delivery_slots,
                sidelines,
                delivery_address,
                fulfilment_method,
                is_express,
                delivery_instructions,
                notes,
                payment_method,
                delivery_address_id,
            )

            now = datetime.utcnow()
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),
                "order_type": OrderType.MEAL_SUBSCRIPTION,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "created_at": now,
                "updated_at": now,
                **order_payload,
            }

            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id

            subscription_dict = {
                **subscription_payload,
                "order_id": result.inserted_id,
                "user_id": ObjectId(user_id),
                "created_at": now,
                "updated_at": now,
            }

            sub_result = await subscription_collection.insert_one(subscription_dict)
            subscription_dict["_id"] = sub_result.inserted_id

            try:
                # Reminder scheduling is a best-effort helper and should never block checkout.
                await reminder_service.schedule_reminders_for_subscription(
                    subscription_dict["_id"],
                    plan_records,
                    remaining_unfilled,
                )
            except Exception as reminder_error:
                logger.error(
                    "Failed to schedule reminders for subscription %s: %s",
                    subscription_dict.get("_id"),
                    reminder_error,
                    exc_info=True,
                )

            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "sidelines": order_dict.get("sidelines", []),
                "subtotal": order_dict["subtotal"],
                "tax_amount": order_dict.get("tax_amount", 0.0),
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "delivery_instructions": order_dict["delivery_instructions"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "extra_boxes": order_dict.get("extra_boxes", 0),
                "extra_boxes_price": order_dict.get("extra_boxes_price", 0.0),
                "plan_price_total": order_dict.get("plan_price_total", 0.0),
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"],
            }

            logger.info("Meal subscription order created: %s", order_dict["order_number"])
            return OrderModel(**response_dict), MealSubscriptionModel(**subscription_dict)

        except Exception as e:
            logger.error(f"Error creating meal subscription order: {e}")
            raise

    async def update_meal_subscription_order(
        self,
        order_id: str,
        user_id: str,
        plan_selections: List[Dict],
        delivery_slots: List[Dict],
        sidelines: Optional[List[Dict]],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
        delivery_address_id: Optional[str] = None,
        cutoff_override_dates: Optional[Set[str]] = None,
    ) -> OrderModel:
        """Update an existing meal subscription order."""
        if self.orders is None or self.db is None:
            raise ValueError("Database not connected")

        subscription_collection = (
            self.meal_subs if self.meal_subs is not None else self.weekly_subs_legacy
        )
        if subscription_collection is None:
            raise ValueError("Meal subscription collection not available")

        order_filter = {
            "_id": ObjectId(order_id),
            "user_id": ObjectId(user_id),
        }
        existing_order = await self.orders.find_one(order_filter)
        if not existing_order:
            raise ValueError("Order not found")

        if existing_order.get("order_type") != OrderType.MEAL_SUBSCRIPTION:
            raise ValueError("Only meal subscription orders can be edited")

        if existing_order.get("status") in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
            raise ValueError("This order can no longer be edited")

        subscription_filter = {"order_id": ObjectId(order_id)}
        existing_subscription = await subscription_collection.find_one(subscription_filter)

        (
            order_payload,
            subscription_payload,
            plan_records,
            remaining_unfilled,
        ) = await self._prepare_meal_subscription_documents(
            user_id,
            plan_selections,
            delivery_slots,
            sidelines,
            delivery_address,
            fulfilment_method,
            is_express,
            delivery_instructions,
            notes,
            payment_method,
            delivery_address_id,
            existing_subscription,
            cutoff_override_dates,
        )

        now = datetime.utcnow()
        await self.orders.update_one(
            order_filter,
            {
                "$set": {
                    **order_payload,
                    "updated_at": now,
                }
            },
        )

        subscription_dict = {
            **subscription_payload,
            "order_id": ObjectId(order_id),
            "user_id": ObjectId(user_id),
            "created_at": existing_subscription.get("created_at") if existing_subscription else now,
            "updated_at": now,
        }

        if existing_subscription:
            await subscription_collection.update_one(
                subscription_filter,
                {"$set": subscription_dict},
            )
            subscription_id = existing_subscription["_id"]
        else:
            insert_result = await subscription_collection.insert_one(subscription_dict)
            subscription_id = insert_result.inserted_id

        await reminder_service.schedule_reminders_for_subscription(
            subscription_id,
            plan_records,
            remaining_unfilled,
        )

        updated = await self.get_order_by_id(order_id)
        if not updated:
            raise ValueError("Failed to load updated order")

        try:
            await notification_service.send_meal_plan_update_notifications(updated)
        except Exception as notify_error:
            logger.warning(
                "Meal plan update notification failed for order %s: %s",
                order_id,
                notify_error,
        )

        return updated

    async def update_delivery_slot_menu_items(
        self,
        order_id: str,
        actor_user_id: str,
        delivery_date: str,
        menu_items: Dict[str, int],
        notes: Optional[str],
        override_cutoff: bool = False,
        actor_role: str = "user",
    ) -> OrderModel:
        """
        Update menu items for a specific delivery date on a meal subscription.

        Customers are blocked after cutoff; admins may override with `override_cutoff=True`.
        """
        if self.orders is None or self.db is None:
            raise ValueError("Database not connected")

        subscription_collection = (
            self.meal_subs if self.meal_subs is not None else self.weekly_subs_legacy
        )
        if subscription_collection is None:
            raise ValueError("Meal subscription collection not available")

        order = await self.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise ValueError("Order not found")

        order_user_id = str(order.get("user_id"))
        if actor_role != "admin" and order_user_id != str(actor_user_id):
            raise ValueError("You are not allowed to edit this order")

        subscription = await subscription_collection.find_one({"order_id": ObjectId(order_id)})
        if not subscription:
            raise ValueError("Meal subscription not found")

        normalized_items: Dict[str, int] = {}
        for item_id, qty in menu_items.items():
            str_id = str(item_id).strip()
            try:
                int_qty = int(qty)
            except (TypeError, ValueError):
                int_qty = 0
            if not str_id or int_qty <= 0:
                continue
            normalized_items[str_id] = int_qty
        if not normalized_items:
            raise ValueError("Please include at least one menu item with a quantity")

        delivery_slots_payload: List[Dict[str, Any]] = []
        target_found = False
        for slot in subscription.get("delivery_slots", []):
            raw_date = slot.get("delivery_date")
            date_key = (
                raw_date.strftime("%Y-%m-%d")
                if isinstance(raw_date, datetime)
                else str(raw_date)
            )
            slot_payload = {
                "delivery_date": date_key,
                "menu_items": slot.get("menu_items", {}),
                "notes": slot.get("notes"),
            }

            if date_key == delivery_date:
                target_found = True
                slot_payload["menu_items"] = normalized_items
                if notes is not None:
                    slot_payload["notes"] = notes

            delivery_slots_payload.append(slot_payload)

        if not target_found:
            raise ValueError("Delivery date not found on this subscription")

        override_dates = {delivery_date} if override_cutoff else None

        delivery_method = order.get("delivery_method", "delivery")
        fulfilment_method = "pickup" if delivery_method == "pickup" else "delivery"
        is_express = delivery_method == "express"

        return await self.update_meal_subscription_order(
            order_id,
            order_user_id,
            subscription.get("plan_selections", []),
            delivery_slots_payload,
            order.get("sidelines"),
            order.get("delivery_address"),
            fulfilment_method,
            is_express,
            order.get("delivery_instructions"),
            order.get("notes"),
            order.get("payment_method", "cash"),
            order.get("delivery_address_id"),
            override_dates,
        )

    async def get_meal_subscription_details(
        self,
        order_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return subscription-specific metadata for a meal subscription order."""
        if self.orders is None:
            return None

        order = await self.orders.find_one(
            {"_id": ObjectId(order_id), "user_id": ObjectId(user_id)}
        )
        if not order:
            return None

        if order.get("order_type") != OrderType.MEAL_SUBSCRIPTION:
            raise ValueError("Only meal subscription orders contain schedule data")

        subscription_collection = (
            self.meal_subs if self.meal_subs is not None else self.weekly_subs_legacy
        )
        if subscription_collection is None:
            return None

        subscription = await subscription_collection.find_one(
            {"order_id": ObjectId(order_id)}
        )
        if not subscription:
            return None

        plan_selections = []
        plan_price_total = subscription.get("plan_price_total") or order.get("plan_price_total") or 0.0
        extra_boxes = subscription.get("extra_boxes") or order.get("extra_boxes") or 0
        extra_boxes_price = subscription.get("extra_boxes_price") or order.get("extra_boxes_price") or 0.0
        for selection in subscription.get("plan_selections", []):
            plan_selections.append(
                {
                    "plan_id": selection.get("plan_id"),
                    "plan_code": selection.get("plan_code"),
                    "plan_name": selection.get("plan_name"),
                    "quantity": selection.get("quantity", 1),
                }
            )

        delivery_slots = []
        business_tz = get_business_timezone()
        now_local = get_business_now().astimezone(business_tz)
        for slot in subscription.get("delivery_slots", []):
            date_val = slot.get("delivery_date")
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)

            cutoff_at = slot.get("cutoff_at")
            cutoff_local = None
            if cutoff_at:
                try:
                    cutoff_local = cutoff_at.astimezone(business_tz)
                except Exception:
                    cutoff_local = None
            if cutoff_local is None:
                try:
                    cutoff_local = datetime.combine(
                        datetime.fromisoformat(date_str).date(),
                        time(hour=0, minute=5),
                        tzinfo=business_tz,
                    )
                except Exception:
                    cutoff_local = None
            cutoff_iso = (
                cutoff_local.astimezone(timezone.utc).isoformat()
                if cutoff_local is not None
                else None
            )

            locked_at = slot.get("locked_at")
            is_locked = locked_at is not None
            if cutoff_local is not None and not is_locked:
                is_locked = now_local >= cutoff_local

            delivery_slots.append(
                {
                    "delivery_date": date_str,
                    "menu_items": slot.get("menu_items", {}),
                    "notes": slot.get("notes"),
                    "cutoff_at": cutoff_iso,
                    "is_locked": bool(is_locked),
                }
            )

        return {
            "order_id": str(order["_id"]),
            "order_number": order.get("order_number"),
            "plan_selections": plan_selections,
            "delivery_slots": delivery_slots,
            "fulfilment_method": subscription.get(
                "fulfilment_type", order.get("delivery_method")
            ),
            "is_express": bool(subscription.get("express_delivery")),
            "delivery_address_id": order.get("delivery_address_id"),
            "delivery_instructions": order.get("delivery_instructions"),
            "notes": order.get("notes"),
            "payment_method": order.get("payment_method"),
            "extra_boxes": extra_boxes,
            "extra_boxes_price": extra_boxes_price,
            "plan_price_total": plan_price_total,
        }

    async def create_catering_order(
        self,
        user_id: str,
        package_type: str,
        guest_count: int,
        event_date: str,
        event_time: str,
        venue_address: str,
        selected_items: Dict[str, List[str]],
        special_requests: str = None,
        payment_method: str = "cash"
    ) -> tuple[OrderModel, CateringOrderModel]:
        """Create catering order"""
        try:
            if self.orders is None or self.catering_orders is None:
                raise ValueError("Database not connected")
                
            # Get package pricing
            price_per_head = {
                "basic": CATERING_BASIC_PRICE,
                "premium": CATERING_PREMIUM_PRICE,
                "diamond": CATERING_DIAMOND_PRICE
            }[package_type]
            
            package_total = price_per_head * guest_count
            
            # Calculate delivery fee (simplified)
            delivery_fee = CATERING_BASE_DELIVERY_FEE
            
            total_amount = package_total + delivery_fee
            advance_payment = total_amount * CATERING_ADVANCE_PAYMENT_PERCENT
            remaining_payment = total_amount - advance_payment
            
            # Build order items from selected items
            order_items = []
            for category, item_ids in selected_items.items():
                for item_id in item_ids:
                    menu_item = await menu_service.get_menu_item_by_id(item_id)
                    if not menu_item:
                        raise ValueError(f"Item {item_id} not found")
                    
                    order_item = OrderItem(
                        item_id=str(menu_item.id),
                        item_name=menu_item.name,
                        category=category,
                        quantity=guest_count,
                        price=price_per_head,
                        subtotal=package_total
                    )
                    order_items.append(order_item)
            
            # Create order document
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),
                "order_type": OrderType.CATERING,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "payment_method": (payment_method or "cash").lower(),
                "items": [item.dict() for item in order_items],
                "subtotal": package_total,
                "delivery_fee": delivery_fee,
                "total_amount": total_amount,
                "delivery_method": "standard",
                "delivery_address": {"street": venue_address},
                "notes": special_requests,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id
            
            # Create catering record
            event_date_parsed = parse_date(event_date)
            
            catering_dict = {
                "order_id": result.inserted_id,
                "user_id": ObjectId(user_id),
                "event_date": event_date_parsed,
                "event_time": event_time,
                "venue_address": venue_address,
                "guest_count": guest_count,
                "package_type": package_type,
                "package_price_per_head": price_per_head,
                "selected_items": selected_items,
                "package_total": package_total,
                "delivery_fee": delivery_fee,
                "advance_payment_amount": advance_payment,
                "remaining_payment_amount": remaining_payment,
                "advance_paid": False,
                "final_paid": False,
                "quote_sent": False,
                "quote_accepted": False,
                "special_requests": special_requests,
                "created_at": datetime.utcnow()
            }
            
            cat_result = await self.catering_orders.insert_one(catering_dict)
            catering_dict["_id"] = cat_result.inserted_id
            
            # Convert ObjectIds to strings for response
            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "sidelines": order_dict.get("sidelines", []),
                "subtotal": order_dict["subtotal"],
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"]
            }
            
            logger.info(f"Catering order created: {order_dict['order_number']}")
            return OrderModel(**response_dict), CateringOrderModel(**catering_dict)
            
        except Exception as e:
            logger.error(f"Error creating catering order: {e}")
            raise
    
    async def get_order_by_id(self, order_id: str) -> Optional[OrderModel]:
        """Get order by ID"""
        try:
            if self.orders is None:
                return None
                
            order = await self.orders.find_one({"_id": ObjectId(order_id)})
            if order:
                # Convert ObjectIds to strings
                order["_id"] = str(order["_id"])
                order["user_id"] = str(order["user_id"])
                return OrderModel(**order)
            return None
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None
    
    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20) -> tuple[List[OrderModel], int]:
        """Get user's orders with pagination metadata."""
        try:
            if self.orders is None:
                return [], 0

            query = {"user_id": ObjectId(user_id)}
            total = await self.orders.count_documents(query)

            cursor = (
                self.orders.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )

            orders = await cursor.to_list(length=limit)

            result: List[OrderModel] = []
            for order in orders:
                order["_id"] = str(order["_id"])
                order["user_id"] = str(order["user_id"])
                result.append(OrderModel(**order))

            return result, total

        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return [], 0
    
    async def update_order_status(self, order_id: str, status: str, admin_notes: str = None) -> OrderModel:
        """Update order status"""
        try:
            if self.orders is None:
                raise ValueError("Database not connected")
                
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if admin_notes:
                update_data["admin_notes"] = admin_notes
            
            if status == OrderStatus.DELIVERED:
                update_data["delivered_at"] = datetime.utcnow()
            
            await self.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            
            order = await self.get_order_by_id(order_id)
            logger.info(f"Order status updated: {order_id} -> {status}")
            return order
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise
    
    async def update_payment_status(self, order_id: str, payment_status: str, payment_intent_id: str = None) -> OrderModel:
        """Update payment status"""
        try:
            if self.orders is None:
                raise ValueError("Database not connected")
                
            update_data = {
                "payment_status": payment_status,
                "updated_at": datetime.utcnow()
            }
            
            if payment_intent_id:
                update_data["stripe_payment_intent_id"] = payment_intent_id
            
            if payment_status == PaymentStatus.PAID:
                # Get the order first to get total amount
                order = await self.get_order_by_id(order_id)
                if order:
                    update_data["paid_amount"] = order.total_amount
                update_data["status"] = OrderStatus.CONFIRMED
            
            await self.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            
            order = await self.get_order_by_id(order_id)
            logger.info(f"Payment status updated: {order_id} -> {payment_status}")
            return order
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            raise

order_service = OrderService()
