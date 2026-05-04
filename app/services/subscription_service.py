from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from bson import ObjectId

from app.config.database import get_database
from app.models.subscription import MealSubscriptionPlanModel
from app.models.menu import MenuItemModel
from app.services.menu_service import menu_service
from app.schemas.subscription import VALID_DELIVERY_DAYS
from app.utils.constants import LEGACY_DEFAULT_PLAN_CODES
import logging

logger = logging.getLogger(__name__)


class MealSubscriptionService:
    """Service layer for managing meal subscription plans and metadata."""

    def __init__(self):
        self._db = None
        self._plans_collection = None
        self._subscriptions_collection = None

    async def purge_legacy_defaults(self) -> int:
        """Remove any legacy default plans by code."""
        if self.plans is None or not LEGACY_DEFAULT_PLAN_CODES:
            return 0
        result = await self.plans.delete_many({"code": {"$in": LEGACY_DEFAULT_PLAN_CODES}})
        return result.deleted_count or 0

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def plans(self):
        if self._plans_collection is None and self.db is not None:
            self._plans_collection = self.db.meal_subscription_plans
        return self._plans_collection

    @property
    def subscriptions(self):
        if self._subscriptions_collection is None and self.db is not None:
            self._subscriptions_collection = self.db.meal_subscriptions
        return self._subscriptions_collection

    def _normalize_plan_doc(self, doc: Dict[str, Any]) -> None:
        """Ensure delivery day metadata and menu mappings are normalized."""
        raw_days = doc.get("available_delivery_days") or []
        normalized_days: List[str] = []
        for day in raw_days:
            if day is None:
                continue
            normalized = str(day).strip().lower()
            if normalized in VALID_DELIVERY_DAYS and normalized not in normalized_days:
                normalized_days.append(normalized)
        doc["available_delivery_days"] = normalized_days

        raw_mapping = doc.get("menu_item_ids_by_day") or {}
        normalized_mapping: Dict[str, List[str]] = {}
        for raw_day, item_ids in raw_mapping.items():
            if raw_day is None:
                continue
            day = str(raw_day).strip().lower()
            if day not in VALID_DELIVERY_DAYS:
                continue
            if not isinstance(item_ids, list):
                continue
            normalized_ids: List[str] = []
            for item_id in item_ids:
                if item_id is None:
                    continue
                if isinstance(item_id, ObjectId):
                    normalized_ids.append(str(item_id))
                else:
                    normalized_ids.append(str(item_id))
            normalized_mapping[day] = normalized_ids
        doc["menu_item_ids_by_day"] = normalized_mapping

        if not doc["available_delivery_days"] and normalized_mapping:
            doc["available_delivery_days"] = list(normalized_mapping.keys())

        # Normalize delivery-date specific mappings (YYYY-MM-DD)
        raw_date_mapping = doc.get("menu_item_ids_by_delivery_date") or {}
        normalized_date_mapping: Dict[str, List[str]] = {}
        for raw_date, item_ids in raw_date_mapping.items():
            if raw_date is None:
                continue
            date_str = str(raw_date).strip()
            try:
                parsed = datetime.fromisoformat(date_str)
            except Exception:
                continue
            # Only allow Monday (0) and Thursday (3)
            if parsed.weekday() not in (0, 3):
                continue
            if not isinstance(item_ids, list):
                continue
            normalized_ids: List[str] = []
            for item_id in item_ids:
                if item_id is None:
                    continue
                if isinstance(item_id, ObjectId):
                    normalized_ids.append(str(item_id))
                else:
                    normalized_ids.append(str(item_id))
            normalized_date_mapping[date_str] = normalized_ids
        doc["menu_item_ids_by_delivery_date"] = normalized_date_mapping

        terms = doc.get("terms_and_conditions")
        if isinstance(terms, list):
            doc["terms_and_conditions"] = [
                str(term).strip() for term in terms if str(term).strip()
            ]
        elif terms:
            doc["terms_and_conditions"] = [str(terms).strip()]
        else:
            doc["terms_and_conditions"] = []

        # Normalize metadata
        metadata = doc.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        menu_scope = metadata.get("menu_item_scope") or "meal_plan_only"
        menu_scope = (
            menu_scope.strip().lower()
            if isinstance(menu_scope, str)
            else "meal_plan_only"
        )
        if menu_scope not in {"meal_plan_only", "all_menu_items"}:
            menu_scope = "meal_plan_only"
        metadata["menu_item_scope"] = menu_scope
        doc["metadata"] = metadata

        # Normalize notification settings
        notifications = doc.get("customer_notifications") or {}
        upsell_condition = notifications.get("upsell_condition") or "always"
        if not isinstance(upsell_condition, str):
            upsell_condition = "always"
        upsell_condition = upsell_condition.strip().lower()
        if upsell_condition not in {
            "always",
            "when_plan_selected",
            "when_no_plan",
            "hidden",
        }:
            upsell_condition = "always"
        notifications["upsell_condition"] = upsell_condition
        doc["customer_notifications"] = notifications

        # Normalize reminder settings
        reminder_settings = doc.get("reminder_settings")
        if reminder_settings:
            normalized_reminder = {
                "enabled": bool(reminder_settings.get("enabled", False)),
                "frequency_days": int(
                    reminder_settings.get("frequency_days", 7) or 7
                ),
                "channel": (
                    str(reminder_settings.get("channel", "in_app")).strip().lower()
                    or "in_app"
                ),
                "threshold_unselected_boxes": reminder_settings.get(
                    "threshold_unselected_boxes"
                ),
            }
            if normalized_reminder["frequency_days"] < 1:
                normalized_reminder["frequency_days"] = 1
            if normalized_reminder["frequency_days"] > 30:
                normalized_reminder["frequency_days"] = 30
            if normalized_reminder["channel"] not in {"in_app", "email", "both"}:
                normalized_reminder["channel"] = "in_app"
            threshold = normalized_reminder["threshold_unselected_boxes"]
            if threshold is not None:
                try:
                    threshold_value = int(threshold)
                    normalized_reminder["threshold_unselected_boxes"] = max(
                        threshold_value, 0
                    )
                except (ValueError, TypeError):
                    normalized_reminder["threshold_unselected_boxes"] = None
            doc["reminder_settings"] = normalized_reminder
        else:
            doc["reminder_settings"] = None

        # Ensure is_active defaults to True if missing
        if "is_active" not in doc or doc["is_active"] is None:
            doc["is_active"] = True

    def _menu_item_to_response_dict(self, item: MenuItemModel) -> Dict[str, Any]:
        """Convert a menu item model into the response structure expected by clients."""
        created_at = (
            item.created_at.isoformat()
            if isinstance(item.created_at, datetime)
            else str(item.created_at)
        )
        updated_at = (
            item.updated_at.isoformat()
            if isinstance(item.updated_at, datetime)
            else str(item.updated_at)
        )

        return {
            "id": str(item.id),
            "_id": str(item.id),
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "price": item.price,
            "image_url": getattr(item, "image_url", None),
            "is_available": getattr(item, "is_available", True),
            "is_available_for_daily": getattr(item, "is_available_for_daily", False),
            "is_available_for_meal_plan": getattr(item, "is_available_for_meal_plan", False),
            "allergens": item.allergens or [],
            "spice_level": item.spice_level,
            "is_vegetarian": getattr(item, "is_vegetarian", False),
            "is_vegan": getattr(item, "is_vegan", False),
            "is_halal": getattr(item, "is_halal", True),
            "nutritional_info": getattr(item, "nutritional_info", None),
            "serving_size": getattr(item, "serving_size", None),
            "created_at": created_at,
            "updated_at": updated_at,
        }

    async def _attach_menu_items(self, plan_docs: List[Dict[str, Any]]) -> None:
        """Attach detailed menu information to each plan document."""
        unique_ids: Dict[str, None] = {}
        for doc in plan_docs:
            mapping = doc.get("menu_item_ids_by_day") or {}
            for item_ids in mapping.values():
                for item_id in item_ids or []:
                    unique_ids[str(item_id)] = None
            date_mapping = doc.get("menu_item_ids_by_delivery_date") or {}
            for item_ids in date_mapping.values():
                for item_id in item_ids or []:
                    unique_ids[str(item_id)] = None

        if not unique_ids:
            for doc in plan_docs:
                doc.setdefault("menu_items_by_day", {})
                doc.setdefault("menu_items_by_delivery_date", {})
            return

        menu_items = await menu_service.get_menu_items_by_ids(list(unique_ids.keys()))
        lookup: Dict[str, Dict[str, Any]] = {}
        for item in menu_items:
            if not item or item.id is None:
                continue
            lookup[str(item.id)] = self._menu_item_to_response_dict(item)

        for doc in plan_docs:
            mapping = doc.get("menu_item_ids_by_day") or {}
            enriched: Dict[str, List[Dict[str, Any]]] = {}
            for day, item_ids in mapping.items():
                if not isinstance(item_ids, list):
                    continue
                enriched[day] = [
                    lookup[item_id] for item_id in item_ids if item_id in lookup
                ]
            doc["menu_items_by_day"] = enriched

            date_mapping = doc.get("menu_item_ids_by_delivery_date") or {}
            enriched_dates: Dict[str, List[Dict[str, Any]]] = {}
            for delivery_date, item_ids in date_mapping.items():
                if not isinstance(item_ids, list):
                    continue
                enriched_dates[delivery_date] = [
                    lookup[item_id] for item_id in item_ids if item_id in lookup
                ]
            doc["menu_items_by_delivery_date"] = enriched_dates

    async def list_plans(
        self,
        tab: Optional[str] = None,
        include_inactive: bool = False,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[MealSubscriptionPlanModel], int]:
        """Return plans filtered by tab and activity with pagination support."""
        if self.plans is None:
            return [], 0

        query: Dict[str, Any] = {}
        if tab:
            query["tab"] = tab
        if not include_inactive:
            query["$or"] = [
                {"is_active": True},
                {"is_active": {"$exists": False}},
            ]

        skip = max(0, (page - 1) * page_size)
        total = await self.plans.count_documents(query)

        cursor = (
            self.plans.find(query)
            .sort("display_order", 1)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        for doc in results:
            self._normalize_plan_doc(doc)

        await self._attach_menu_items(results)

        plans: List[MealSubscriptionPlanModel] = []
        for doc in results:
            doc["_id"] = str(doc["_id"])
            plans.append(MealSubscriptionPlanModel(**doc))
        return plans, total

    async def get_plan_by_id(self, plan_id: str) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return None

        doc = await self.plans.find_one({"_id": ObjectId(plan_id)})
        if not doc:
            return None
        self._normalize_plan_doc(doc)
        await self._attach_menu_items([doc])
        doc["_id"] = str(doc["_id"])
        return MealSubscriptionPlanModel(**doc)

    async def get_plan_by_code(self, code: str) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None:
            return None

        doc = await self.plans.find_one({"code": code})
        if not doc:
            return None
        self._normalize_plan_doc(doc)
        await self._attach_menu_items([doc])
        doc["_id"] = str(doc["_id"])
        return MealSubscriptionPlanModel(**doc)

    async def create_plan(self, plan_data: Dict[str, Any]) -> MealSubscriptionPlanModel:
        if self.plans is None:
            raise ValueError("Meal subscription plans collection not available")

        now = datetime.utcnow()

        normalized_code = plan_data.get("code")
        if normalized_code:
            normalized_code = normalized_code.strip().lower().replace(" ", "_")

        # Prevent duplicate codes
        if normalized_code:
            existing = await self.plans.find_one({"code": normalized_code})
            if existing:
                raise ValueError(f"Plan code '{normalized_code}' already exists")

        plan_doc = {
            **plan_data,
            "created_at": now,
            "updated_at": now,
        }
        if normalized_code:
            plan_doc["code"] = normalized_code

        self._normalize_plan_doc(plan_doc)
        result = await self.plans.insert_one(plan_doc)
        plan_doc["_id"] = str(result.inserted_id)
        await self._attach_menu_items([plan_doc])
        logger.info("Meal subscription plan created: %s", plan_doc["code"])
        return MealSubscriptionPlanModel(**plan_doc)

    async def update_plan(self, plan_id: str, update_data: Dict[str, Any]) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return None

        update_payload = {k: v for k, v in update_data.items() if v is not None}
        if not update_payload:
            return await self.get_plan_by_id(plan_id)

        if "code" in update_payload and update_payload["code"]:
            normalized_code = (
                update_payload["code"].strip().lower().replace(" ", "_")
            )
            update_payload["code"] = normalized_code

            if self.plans is not None:
                existing = await self.plans.find_one(
                    {"code": normalized_code, "_id": {"$ne": ObjectId(plan_id)}}
                )
                if existing:
                    raise ValueError(f"Plan code '{normalized_code}' already exists")

        if (
            "available_delivery_days" in update_payload
            or "menu_item_ids_by_day" in update_payload
            or "menu_item_ids_by_delivery_date" in update_payload
        ):
            temp_doc = {
                "available_delivery_days": update_payload.get(
                    "available_delivery_days", []
                ),
                "menu_item_ids_by_day": update_payload.get(
                    "menu_item_ids_by_day", {}
                ),
                "menu_item_ids_by_delivery_date": update_payload.get(
                    "menu_item_ids_by_delivery_date", {}
                ),
            }
            self._normalize_plan_doc(temp_doc)
            if "available_delivery_days" in update_payload:
                update_payload["available_delivery_days"] = temp_doc[
                    "available_delivery_days"
                ]
            if "menu_item_ids_by_day" in update_payload:
                update_payload["menu_item_ids_by_day"] = temp_doc[
                    "menu_item_ids_by_day"
                ]
            if "menu_item_ids_by_delivery_date" in update_payload:
                update_payload["menu_item_ids_by_delivery_date"] = temp_doc[
                    "menu_item_ids_by_delivery_date"
                ]

        if "terms_and_conditions" in update_payload:
            terms = update_payload.get("terms_and_conditions") or []
            update_payload["terms_and_conditions"] = [
                str(term).strip() for term in terms if str(term).strip()
            ]

        # Prevent immutable fields from being updated
        update_payload.pop("_id", None)
        update_payload.pop("id", None)

        update_payload["updated_at"] = datetime.utcnow()

        result = await self.plans.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": update_payload}
        )
        if result.matched_count == 0:
            return None
        return await self.get_plan_by_id(plan_id)

    async def delete_plan(self, plan_id: str) -> bool:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return False

        result = await self.plans.delete_one({"_id": ObjectId(plan_id)})
        return result.deleted_count > 0


meal_subscription_service = MealSubscriptionService()
