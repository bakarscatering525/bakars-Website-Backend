from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.config.database import get_database
from app.services.notification_service import notification_service
from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self):
        self._db = None
        self._subscriptions = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def subscriptions(self):
        if self._subscriptions is None and self.db is not None:
            self._subscriptions = self.db.meal_subscriptions
        return self._subscriptions

    @staticmethod
    def _resolve_plan_settings(plan_records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for record in plan_records:
            plan = record.get("plan")
            if not plan:
                continue
            settings = getattr(plan, "reminder_settings", None) or record.get("reminder_settings")
            enabled = getattr(settings, "enabled", False)
            if isinstance(settings, dict):
                enabled = settings.get("enabled", False)
            if not enabled:
                continue
            if hasattr(settings, "model_dump"):
                return settings.model_dump()
            return dict(settings)
        return None

    async def schedule_reminders_for_subscription(
        self,
        subscription_id: ObjectId,
        plan_records: List[Dict[str, Any]],
        remaining_boxes: int,
    ) -> None:
        if self.subscriptions is None:
            return

        settings = self._resolve_plan_settings(plan_records)
        if not settings or not settings.get("enabled"):
            return

        threshold = settings.get("threshold_unselected_boxes") or 0
        if remaining_boxes <= threshold:
            return

        frequency_days = max(int(settings.get("frequency_days", 7)), 1)
        next_reminder_at = datetime.utcnow() + timedelta(days=frequency_days)

        await self.subscriptions.update_one(
            {"_id": subscription_id},
            {
                "$set": {
                    "reminder_settings": settings,
                    "next_reminder_at": next_reminder_at,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    async def process_due_reminders(self) -> int:
        if self.subscriptions is None:
            return 0

        now = datetime.utcnow()
        cursor = self.subscriptions.find(
            {
                "is_active": True,
                "next_reminder_at": {"$lte": now},
                "reminder_settings.enabled": True,
            }
        ).limit(100)

        due_subscriptions = await cursor.to_list(length=100)
        processed = 0

        for subscription in due_subscriptions:
            try:
                total_included = subscription.get("total_included_boxes", 0)
                total_selected = subscription.get("total_selected_boxes", 0)
                remaining = max(total_included - total_selected, 0)

                settings = subscription.get("reminder_settings") or {}
                threshold = settings.get("threshold_unselected_boxes") or 0

                if remaining <= threshold:
                    await self.subscriptions.update_one(
                        {"_id": subscription["_id"]},
                        {"$set": {"next_reminder_at": None}},
                    )
                    continue

                sent = await self._send_reminder(subscription, remaining)
                if not sent:
                    continue

                frequency_days = max(int(settings.get("frequency_days", 7)), 1)
                next_time = now + timedelta(days=frequency_days)

                await self.subscriptions.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "next_reminder_at": next_time,
                            "updated_at": datetime.utcnow(),
                        },
                        "$push": {"reminders_sent": now.isoformat()},
                    },
                )
                processed += 1
            except Exception as exc:
                logger.error("Failed to process reminder: %s", exc, exc_info=True)

        return processed

    async def _send_reminder(self, subscription: Dict[str, Any], remaining: int) -> bool:
        try:
            user = await auth_service.get_user_by_id(str(subscription["user_id"]))
            if not user:
                logger.warning("Skipping reminder; user missing for subscription %s.", subscription.get("_id"))
                return False

            plan_names = [selection.get("plan_code") for selection in subscription.get("plan_selections", [])]
            plan_summary = ", ".join(filter(None, plan_names)) or "your meal plan"

            reminder_settings = subscription.get("reminder_settings") or {}
            channel = str(reminder_settings.get("channel") or "in_app").lower()
            if channel not in {"in_app", "email", "both"}:
                channel = "in_app"

            first_name = getattr(user, "first_name", None) or getattr(user, "full_name", None)
            greeting = first_name or getattr(user, "email", None) or "there"

            message = (
                f"Hi {greeting}, you still have {remaining} box(es) to assign for {plan_summary}. "
                "Jump back in to finish your selections before the weekly cut-off."
            )
            title = "Meal plan reminder"
            metadata = {
                "plan_codes": [code for code in plan_names if code],
                "remaining_boxes": remaining,
            }
            if subscription.get("_id"):
                metadata["subscription_id"] = str(subscription["_id"])

            delivery_results: List[bool] = []

            if channel in {"in_app", "both"}:
                delivery_results.append(
                    await notification_service.send_in_app_notification(
                        user_id=str(subscription.get("user_id")),
                        title=title,
                        message=message,
                        metadata=metadata,
                    )
                )

            if channel in {"email", "both"}:
                delivery_results.append(
                    await notification_service.send_email_notification(
                        getattr(user, "email", None),
                        subject=title,
                        message=message,
                    )
                )

            if not any(delivery_results):
                phone = getattr(user, "phone", None)
                if phone:
                    logger.info(
                        "Reminder channel %s unavailable for user %s; falling back to WhatsApp.",
                        channel,
                        getattr(user, "id", None) or subscription.get("user_id"),
                    )
                    delivery_results.append(
                        await notification_service.send_whatsapp_message(phone, message)
                    )
                else:
                    logger.warning(
                        "Unable to deliver reminder for user %s; no valid contact methods found.",
                        getattr(user, "id", None) or subscription.get("user_id"),
                    )

            return any(delivery_results)
        except Exception as exc:
            logger.error("Failed to send reminder notification: %s", exc, exc_info=True)
            return False


reminder_service = ReminderService()
