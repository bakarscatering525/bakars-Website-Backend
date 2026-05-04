from typing import List, Optional, Tuple, Dict, Any, Set
from bson import ObjectId
from datetime import datetime
from app.config.database import database
from app.models.menu import MenuItemModel, CategoryModel, WeeklyMenuScheduleModel
import logging

logger = logging.getLogger(__name__)

ADD_ONS_CATEGORY_ALIASES = {
    "add ons",
    "addons",
    "add on",
}
ADD_ONS_CATEGORY_REGEX = r"^add[\s\-_]*ons?$"

class MenuService:
    """Service layer for menu operations"""

    @staticmethod
    def _normalize_category_value(value: Optional[str]) -> str:
        if not value:
            return ""
        normalized = value.lower()
        for char in ("_", "-", "'"):
            normalized = normalized.replace(char, " ")
        normalized = " ".join(normalized.split())
        return normalized

    def _is_addons_category(self, value: Optional[str]) -> bool:
        normalized = self._normalize_category_value(value)
        return normalized in ADD_ONS_CATEGORY_ALIASES

    def _addons_regex_condition(self) -> Dict[str, Any]:
        return {"$regex": ADD_ONS_CATEGORY_REGEX, "$options": "i"}

    @staticmethod
    def _build_variant_group_key(item: Dict[str, Any]) -> Tuple[str, str, float, str]:
        """Create a grouping key to identify legacy duplicate program variants."""
        name = str(item.get("name") or "").strip().lower()
        category = str(item.get("category") or "").strip().lower()
        description = str(item.get("description") or "").strip().lower()
        price_raw = item.get("price", 0)
        try:
            price = float(price_raw or 0)
        except (TypeError, ValueError):
            price = 0.0
        return (name, category, price, description)

    @staticmethod
    def _deduplicate_ordered(values: List[Any]) -> List[Any]:
        """Remove duplicates from a list while preserving order."""
        seen: Set[str] = set()
        deduped: List[Any] = []
        for value in values:
            key = str(value)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)
        return deduped

    async def _replace_ids_in_weekly_schedule(self, replacements: Dict[str, str]) -> int:
        """Update weekly menu schedules to point to the consolidated menu item IDs."""
        if self.weekly_schedule is None or not replacements:
            return 0

        object_id_map: Dict[ObjectId, ObjectId] = {}
        for old_id, new_id in replacements.items():
            if ObjectId.is_valid(old_id) and ObjectId.is_valid(new_id):
                object_id_map[ObjectId(old_id)] = ObjectId(new_id)

        if not object_id_map:
            return 0

        cursor = self.weekly_schedule.find({"menu_items": {"$in": list(object_id_map.keys())}})
        schedules = await cursor.to_list(length=None)
        updated = 0

        for schedule in schedules:
            original_items = schedule.get("menu_items", []) or []
            new_items: List[ObjectId] = []
            changed = False

            for item_id in original_items:
                replacement = object_id_map.get(item_id)
                if replacement is not None:
                    new_items.append(replacement)
                    changed = True
                else:
                    new_items.append(item_id)

            if changed:
                deduped_items = self._deduplicate_ordered(new_items)
                await self.weekly_schedule.update_one(
                    {"_id": schedule["_id"]},
                    {"$set": {"menu_items": deduped_items, "updated_at": datetime.utcnow()}},
                )
                updated += 1

        return updated

    async def _replace_ids_in_meal_plans(self, replacements: Dict[str, str]) -> int:
        """Update meal plan templates to use the consolidated menu item IDs."""
        if self.meal_plans is None or not replacements:
            return 0

        cursor = self.meal_plans.find({"menu_item_ids_by_day": {"$exists": True}})
        plans = await cursor.to_list(length=None)
        updated = 0

        for plan in plans:
            mapping = plan.get("menu_item_ids_by_day") or {}
            changed = False

            for day, item_ids in mapping.items():
                if not isinstance(item_ids, list):
                    continue
                day_changed = False
                new_ids: List[str] = []
                for item_id in item_ids:
                    replacement = replacements.get(str(item_id))
                    if replacement:
                        new_ids.append(replacement)
                        day_changed = True
                    else:
                        new_ids.append(str(item_id))

                if day_changed:
                    mapping[day] = self._deduplicate_ordered(new_ids)
                    changed = True

            if changed:
                await self.meal_plans.update_one(
                    {"_id": plan["_id"]},
                    {
                        "$set": {
                            "menu_item_ids_by_day": mapping,
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )
                updated += 1

        return updated

    async def _replace_ids_in_meal_subscriptions(self, replacements: Dict[str, str]) -> int:
        """Update active meal subscriptions so their slots point to consolidated IDs."""
        if self.meal_subscriptions is None or not replacements:
            return 0

        cursor = self.meal_subscriptions.find({"delivery_slots": {"$exists": True, "$ne": []}})
        subscriptions = await cursor.to_list(length=None)
        updated = 0

        for subscription in subscriptions:
            slots = subscription.get("delivery_slots") or []
            subscription_changed = False

            for slot in slots:
                slot_items = slot.get("menu_items") or {}
                if not isinstance(slot_items, dict) or not slot_items:
                    continue

                new_slot_items: Dict[str, int] = {}
                slot_changed = False

                for item_id, quantity in slot_items.items():
                    str_id = str(item_id)
                    replacement = replacements.get(str_id)
                    if replacement:
                        slot_changed = True
                        subscription_changed = True
                        new_slot_items[replacement] = new_slot_items.get(replacement, 0) + quantity
                    else:
                        new_slot_items[str_id] = new_slot_items.get(str_id, 0) + quantity

                if slot_changed:
                    slot["menu_items"] = new_slot_items

            if subscription_changed:
                await self.meal_subscriptions.update_one(
                    {"_id": subscription["_id"]},
                    {"$set": {"delivery_slots": slots, "updated_at": datetime.utcnow()}},
                )
                updated += 1

        return updated

    async def _update_menu_item_references(self, replacements: Dict[str, str]) -> None:
        """Ensure related collections reference the surviving menu item IDs."""
        if not replacements:
            return

        await self._replace_ids_in_weekly_schedule(replacements)
        await self._replace_ids_in_meal_plans(replacements)
        await self._replace_ids_in_meal_subscriptions(replacements)

    async def consolidate_program_variants(self) -> int:
        """Merge legacy duplicate menu items created for individual programs."""
        if self.menu_items is None:
            logger.warning("Menu items collection not available")
            return 0

        try:
            cursor = self.menu_items.find({})
            documents = await cursor.to_list(length=None)
            if not documents:
                return 0

            grouped: Dict[Tuple[str, str, float, str], List[Dict[str, Any]]] = {}
            for doc in documents:
                key = self._build_variant_group_key(doc)
                grouped.setdefault(key, []).append(doc)

            replacements: Dict[str, str] = {}
            keep_updates: Dict[str, Dict[str, Any]] = {}
            duplicates_to_delete: List[ObjectId] = []

            for variant_docs in grouped.values():
                if len(variant_docs) < 2:
                    continue

                has_daily_variant = any(doc.get("is_available_for_daily") for doc in variant_docs)
                has_meal_variant = any(doc.get("is_available_for_meal_plan") for doc in variant_docs)

                # Only consolidate variants that represent both availability scopes
                if not (has_daily_variant and has_meal_variant):
                    continue

                variant_docs.sort(
                    key=lambda doc: doc.get("created_at")
                    if isinstance(doc.get("created_at"), datetime)
                    else datetime.min
                )

                combined_daily = has_daily_variant
                combined_meal = has_meal_variant
                combined_available = any(doc.get("is_available", True) for doc in variant_docs)

                keep_doc = next(
                    (
                        doc
                        for doc in variant_docs
                        if doc.get("is_available_for_daily") and doc.get("is_available_for_meal_plan")
                    ),
                    None,
                )

                if keep_doc is None:
                    keep_doc = next(
                        (doc for doc in variant_docs if doc.get("is_available_for_daily")),
                        variant_docs[0],
                    )

                keep_id = keep_doc["_id"]
                updates: Dict[str, Any] = {}

                if keep_doc.get("is_available_for_daily", False) != combined_daily:
                    updates["is_available_for_daily"] = combined_daily
                if keep_doc.get("is_available_for_meal_plan", False) != combined_meal:
                    updates["is_available_for_meal_plan"] = combined_meal
                if keep_doc.get("is_available", True) != combined_available:
                    updates["is_available"] = combined_available

                if updates:
                    keep_updates[str(keep_id)] = updates

                for doc in variant_docs:
                    if doc["_id"] == keep_id:
                        continue
                    replacements[str(doc["_id"])] = str(keep_id)
                    duplicates_to_delete.append(doc["_id"])

            if not replacements:
                return 0

            await self._update_menu_item_references(replacements)

            for keep_id_str, payload in keep_updates.items():
                payload["updated_at"] = datetime.utcnow()
                await self.menu_items.update_one(
                    {"_id": ObjectId(keep_id_str)},
                    {"$set": payload},
                )

            if duplicates_to_delete:
                await self.menu_items.delete_many({"_id": {"$in": duplicates_to_delete}})

            logger.info(
                "Consolidated %d legacy program-specific menu item variants",
                len(duplicates_to_delete),
            )
            return len(duplicates_to_delete)
        except Exception as exc:
            logger.error(
                "Failed to consolidate legacy menu item variants: %s",
                exc,
                exc_info=True,
            )
            return 0

    async def _fetch_daily_items_with_addons_last(
        self,
        base_query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Return all daily items with add-ons appended at the end."""
        regex_condition = self._addons_regex_condition()
        non_addons_query = {**base_query, "category": {"$not": regex_condition}}
        addons_query = {**base_query, "category": regex_condition}

        non_cursor = self.menu_items.find(non_addons_query).sort("name", 1)
        addons_cursor = self.menu_items.find(addons_query).sort("name", 1)

        non_items = await non_cursor.to_list(length=None)
        addon_items = await addons_cursor.to_list(length=None)
        return non_items + addon_items

    async def _fetch_daily_items_with_addons_last_paginated(
        self,
        base_query: Dict[str, Any],
        skip: int,
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return a paginated slice while keeping add-ons last overall."""
        regex_condition = self._addons_regex_condition()
        non_addons_query = {**base_query, "category": {"$not": regex_condition}}
        addons_query = {**base_query, "category": regex_condition}

        total = await self.menu_items.count_documents(base_query)
        if total == 0 or skip >= total:
            return [], total

        non_total = await self.menu_items.count_documents(non_addons_query)
        items: List[Dict[str, Any]] = []
        remaining_limit = limit
        remaining_skip = skip

        if non_total > 0 and remaining_limit > 0:
            if remaining_skip < non_total:
                non_skip = remaining_skip
                non_limit = min(remaining_limit, non_total - non_skip)
                non_cursor = (
                    self.menu_items.find(non_addons_query)
                    .sort("name", 1)
                    .skip(non_skip)
                    .limit(non_limit)
                )
                non_items = await non_cursor.to_list(length=non_limit)
                items.extend(non_items)
                remaining_limit -= non_limit
                remaining_skip = 0
            else:
                remaining_skip -= non_total

        if remaining_limit > 0:
            addon_cursor = (
                self.menu_items.find(addons_query)
                .sort("name", 1)
                .skip(max(0, remaining_skip))
                .limit(remaining_limit)
            )
            addon_items = await addon_cursor.to_list(length=remaining_limit)
            items.extend(addon_items)

        return items, total

    @property
    def db(self):
        """Get database instance lazily"""
        return database.db

    @property
    def menu_items(self):
        """Get menu_items collection"""
        if self.db is not None:
            return self.db.menu_items
        return None

    @property
    def categories(self):
        """Get categories collection"""
        if self.db is not None:
            return self.db.categories
        return None

    @property
    def weekly_schedule(self):
        """Get weekly_menu_schedule collection"""
        if self.db is not None:
            return self.db.weekly_menu_schedule
        return None

    @property
    def meal_plans(self):
        """Get meal subscription plans collection"""
        if self.db is not None and hasattr(self.db, "meal_subscription_plans"):
            return self.db.meal_subscription_plans
        return None

    @property
    def meal_subscriptions(self):
        """Get meal subscriptions collection"""
        if self.db is not None and hasattr(self.db, "meal_subscriptions"):
            return self.db.meal_subscriptions
        return None

    # ============= CATEGORY MANAGEMENT METHODS =============

    async def create_category(self, category_data: dict) -> CategoryModel:
        """Create new category"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Check if category with same name exists
            existing = await self.categories.find_one({"name": category_data["name"]})
            if existing:
                raise ValueError(f"Category with name '{category_data['name']}' already exists")

            # Set default sort order if not provided
            if "sort_order" not in category_data or category_data["sort_order"] is None:
                highest = await self.categories.find_one(sort=[("sort_order", -1)])
                category_data["sort_order"] = (highest["sort_order"] + 1) if highest else 1

            # Prepare category document
            category_dict = {
                **category_data,
                "is_active": category_data.get("is_active", True),
                "created_at": datetime.utcnow()
            }

            result = await self.categories.insert_one(category_dict)
            # FIX: Convert ObjectId to string
            category_dict["_id"] = str(result.inserted_id)

            logger.info(f"Category created: {category_data['name']} with ID {result.inserted_id}")
            return CategoryModel(**category_dict)

        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise

    async def update_category(self, category_id: str, update_data: dict) -> Optional[CategoryModel]:
        """Update existing category"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(category_id):
                raise ValueError(f"Invalid category ID format: {category_id}")

            cleaned_data: Dict[str, Any] = {}
            for key, value in update_data.items():
                if value is None:
                    if key == "image_url":
                        cleaned_data[key] = None
                    continue
                cleaned_data[key] = value

            if not cleaned_data:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            if not update_data:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            if not update_data:
                return await self.get_category_by_id(category_id)

            result = await self.categories.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Category not found or no changes made: {category_id}")
                return None

            # Get and return updated category
            category = await self.get_category_by_id(category_id)
            logger.info(f"Category updated: {category_id}")
            return category

        except Exception as e:
            logger.error(f"Error updating category: {e}")
            raise

    async def delete_category(self, category_id: str, permanent: bool = False) -> bool:
        """Delete category (soft delete by default)"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(category_id):
                logger.error(f"Invalid category ID format: {category_id}")
                return False

            if permanent:
                # Permanent delete
                result = await self.categories.delete_one({"_id": ObjectId(category_id)})
                success = result.deleted_count > 0
                if success:
                    logger.info(f"Category permanently deleted: {category_id}")
            else:
                # Soft delete (deactivate)
                result = await self.categories.update_one(
                    {"_id": ObjectId(category_id)},
                    {"$set": {"is_active": False}}
                )
                success = result.modified_count > 0
                if success:
                    logger.info(f"Category deactivated: {category_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False

    async def get_category_by_id(self, category_id: str) -> Optional[CategoryModel]:
        """Get category by ID or name"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return None

            # Check if category_id is ObjectId or string (name)
            if ObjectId.is_valid(category_id):
                category = await self.categories.find_one({"_id": ObjectId(category_id)})
            else:
                # Try to find by name
                category = await self.categories.find_one({"name": category_id})

            if category:
                # Convert ObjectId to string for the model
                if "_id" in category and isinstance(category["_id"], ObjectId):
                    category["_id"] = str(category["_id"])
                return CategoryModel(**category)
            return None

        except Exception as e:
            logger.error(f"Error getting category by ID: {e}")
            return None

    async def get_all_categories(self, include_inactive: bool = False) -> List[CategoryModel]:
        """Get all categories (with option to include inactive)"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return []

            query = {} if include_inactive else {"is_active": True}
            cursor = self.categories.find(query).sort("sort_order", 1)
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []

    async def get_all_categories_paginated(self, include_inactive: bool, skip: int, limit: int):
        """Paginated categories with total count."""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return [], 0

            query = {} if include_inactive else {"is_active": True}
            total = await self.categories.count_documents(query)
            cursor = self.categories.find(query).sort("sort_order", 1).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting paginated categories: {e}")
            return [], 0

    async def update_category_order(self, category_id: str, new_order: int) -> bool:
        """Update category sort order"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            if not ObjectId.is_valid(category_id):
                return False

            # Update the sort order
            result = await self.categories.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": {"sort_order": new_order}}
            )

            success = result.modified_count > 0
            if success:
                logger.info(f"Category order updated: {category_id} -> {new_order}")

            return success

        except Exception as e:
            logger.error(f"Error updating category order: {e}")
            return False

    async def category_has_items(self, category_id: str) -> bool:
        """Check if category has associated menu items"""
        try:
            if self.menu_items is None or self.categories is None:
                return False

            # Get category by ID or name
            category = await self.get_category_by_id(category_id)
            if not category:
                return False

            # Check for menu items with this category
            count = await self.menu_items.count_documents({"category": category.name})
            return count > 0

        except Exception as e:
            logger.error(f"Error checking category items: {e}")
            return False

    # ============= MENU ITEM METHODS =============

    async def get_all_menu_items(self, include_unavailable: bool = False, category: Optional[str] = None) -> List[MenuItemModel]:
        """Get all menu items (admin view)"""
        try:
            await self.consolidate_program_variants()

            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            query = {}
            if not include_unavailable:
                query["is_available"] = True
            if category:
                query["category"] = category

            cursor = self.menu_items.find(query).sort([("category", 1), ("name", 1)])
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting all menu items: {e}")
            return []

    async def get_all_menu_items_paginated(
        self,
        include_unavailable: bool,
        category: Optional[str],
        skip: int,
        limit: int,
        search: Optional[str] = None,
    ):
        """Paginated menu items with total count (admin view)."""
        try:
            await self.consolidate_program_variants()

            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return [], 0

            query = {}
            if not include_unavailable:
                query["is_available"] = True
            if category:
                query["category"] = category
            if search:
                search_term = search.strip()
                if search_term:
                    regex = {"$regex": search_term, "$options": "i"}
                    query["$or"] = [
                        {"name": regex},
                        {"description": regex},
                    ]

            total = await self.menu_items.count_documents(query)
            cursor = self.menu_items.find(query).sort([("category", 1), ("name", 1)]).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting paginated menu items: {e}")
            return [], 0

    async def get_menu_items_stats(self) -> Dict[str, int]:
        """Return aggregate counts for admin dashboard cards."""
        if self.menu_items is None:
            return {
                "total": 0,
                "available": 0,
                "unavailable": 0,
                "daily_ready": 0,
                "weekly_ready": 0,
            }

        base_query: Dict[str, Any] = {}
        total = await self.menu_items.count_documents(base_query)

        available_query = {**base_query, "is_available": True}
        available = await self.menu_items.count_documents(available_query)

        daily_ready_query = {**available_query, "is_available_for_daily": True}
        daily_ready = await self.menu_items.count_documents(daily_ready_query)

        weekly_ready_query = {**available_query, "is_available_for_meal_plan": True}
        weekly_ready = await self.menu_items.count_documents(weekly_ready_query)

        return {
            "total": total,
            "available": available,
            "unavailable": max(total - available, 0),
            "daily_ready": daily_ready,
            "weekly_ready": weekly_ready,
        }

    def _build_daily_menu_query(
        self,
        category: Optional[str] = None,
        is_vegetarian: Optional[bool] = None,
        is_vegan: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {
            "is_available": True,
            "is_available_for_daily": True,
        }
        if category:
            query["category"] = category
        if is_vegetarian is not None:
            query["is_vegetarian"] = is_vegetarian
        if is_vegan is not None:
            query["is_vegan"] = is_vegan
        if search:
            search_term = search.strip()
            if search_term:
                regex = {"$regex": search_term, "$options": "i"}
                query["$or"] = [
                    {"name": regex},
                    {"description": regex},
                ]
        return query

    async def get_daily_menu(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MenuItemModel]:
        """Get daily menu items with optional filters"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            filters = filters or {}
            query = self._build_daily_menu_query(
                category=filters.get("category"),
                is_vegetarian=filters.get("is_vegetarian"),
                is_vegan=filters.get("is_vegan"),
                search=filters.get("search"),
            )

            if filters.get("category"):
                cursor = self.menu_items.find(query).sort("name", 1)
                items = await cursor.to_list(length=None)
            else:
                items = await self._fetch_daily_items_with_addons_last(query)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting daily menu: {e}")
            raise

    async def get_daily_menu_paginated(
        self,
        filters: Optional[Dict[str, Any]],
        skip: int,
        limit: int,
    ) -> Tuple[List[MenuItemModel], int]:
        """Get daily menu items with pagination and total count."""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return [], 0

            filters = filters or {}
            query = self._build_daily_menu_query(
                category=filters.get("category"),
                is_vegetarian=filters.get("is_vegetarian"),
                is_vegan=filters.get("is_vegan"),
                search=filters.get("search"),
            )

            if filters.get("category"):
                total = await self.menu_items.count_documents(query)
                cursor = (
                    self.menu_items.find(query).sort("name", 1).skip(skip).limit(limit)
                )
                items = await cursor.to_list(length=limit)
            else:
                items, total = await self._fetch_daily_items_with_addons_last_paginated(
                    query, skip, limit
                )

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting daily menu (paginated): {e}")
            return [], 0

    async def _get_default_weekly_items(self, limit: int = 18) -> List[MenuItemModel]:
        """Return a generic list of weekly-available menu items (used as fallback)."""
        if self.menu_items is None:
            return []

        cursor = (
            self.menu_items.find(
                {
                    "is_available": True,
                    "is_available_for_meal_plan": True,
                }
            )
            .sort([("updated_at", -1), ("name", 1)])
            .limit(limit)
        )
        items = await cursor.to_list(length=limit)
        for item in items:
            if "_id" in item and isinstance(item["_id"], ObjectId):
                item["_id"] = str(item["_id"])
        return [MenuItemModel(**item) for item in items]

    async def get_weekly_menu(self, delivery_date: str) -> Optional[dict]:
        """Get weekly menu for specific delivery date (falls back to generic items if needed)."""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available for weekly menu")
                return None

            async def _get_weekly_items_from_plan_mapping(
                target_date: str,
            ) -> List[MenuItemModel]:
                """Use the weekly plan's per-date mapping when no schedule exists."""
                if self.meal_plans is None or self.menu_items is None:
                    return []

                plan_query = {
                    "tab": "weekly",
                    f"menu_item_ids_by_delivery_date.{target_date}": {"$exists": True},
                    "$or": [
                        {"is_active": True},
                        {"is_active": {"$exists": False}},
                    ],
                }
                plan_doc = await self.meal_plans.find_one(plan_query)
                if not plan_doc:
                    return []

                mapping = plan_doc.get("menu_item_ids_by_delivery_date") or {}
                raw_ids = mapping.get(target_date) or []
                valid_object_ids: List[ObjectId] = []
                for raw_id in raw_ids:
                    str_id = str(raw_id)
                    if ObjectId.is_valid(str_id):
                        valid_object_ids.append(ObjectId(str_id))

                if not valid_object_ids:
                    return []

                cursor = self.menu_items.find(
                    {
                        "_id": {"$in": valid_object_ids},
                        "is_available": True,
                        "is_available_for_meal_plan": True,
                    }
                )
                raw_items = await cursor.to_list(length=None)
                items: List[MenuItemModel] = []
                for item in raw_items:
                    if "_id" in item and isinstance(item["_id"], ObjectId):
                        item["_id"] = str(item["_id"])
                    items.append(MenuItemModel(**item))

                return items

            date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
            schedule = None
            if self.weekly_schedule is not None:
                schedule = await self.weekly_schedule.find_one(
                    {"delivery_date": date_obj, "is_active": True}
                )
            else:
                logger.warning("Weekly schedule collection missing; using fallback items")

            items: List[MenuItemModel] = []
            schedule_rotation = 0
            if schedule:
                item_ids = [
                    ObjectId(item_id) if isinstance(item_id, str) else item_id
                    for item_id in schedule.get("menu_items", [])
                ]

                if item_ids:
                    cursor = self.menu_items.find(
                        {
                            "_id": {"$in": item_ids},
                            "is_available": True,
                            "is_available_for_meal_plan": True,
                        }
                    )
                    raw_items = await cursor.to_list(length=None)
                    for item in raw_items:
                        if "_id" in item and isinstance(item["_id"], ObjectId):
                            item["_id"] = str(item["_id"])
                        items.append(MenuItemModel(**item))
                schedule_rotation = schedule.get("menu_rotation", 1)

            if not schedule:
                logger.info(
                    "No weekly schedule found for %s; serving fallback weekly items",
                    delivery_date,
                )

            if not items:
                plan_items = await _get_weekly_items_from_plan_mapping(delivery_date)
                if plan_items:
                    logger.info(
                        "Using weekly plan mapping to build menu for %s", delivery_date
                    )
                    items = plan_items
                    schedule_rotation = 1

            if not items:
                fallback_items = await self._get_default_weekly_items()
                if not fallback_items:
                    logger.warning(
                        "Unable to build fallback weekly menu for %s (no weekly items found)",
                        delivery_date,
                    )
                    return None
                items = fallback_items

            return {
                "delivery_date": delivery_date,
                "menu_rotation": schedule_rotation if schedule_rotation else 0,
                "items": items,
            }

        except Exception as e:
            logger.error(f"Error getting weekly menu: {e}")
            raise

    async def get_catering_menu(self) -> List[MenuItemModel]:
        """Catering menu has been discontinued; return an empty list."""
        logger.info("Catering menu request received; returning empty list.")
        return []

    async def get_catering_menu_paginated(self, skip: int, limit: int) -> List[MenuItemModel]:
        """Catering menu has been discontinued; return an empty list."""
        logger.info(
            "Paginated catering menu request received (skip=%s, limit=%s); returning empty list.",
            skip,
            limit,
        )
        return []

    async def get_menu_item_by_id(self, item_id: str) -> Optional[MenuItemModel]:
        """Get specific menu item by ID"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return None

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                logger.error(f"Invalid ObjectId format: {item_id}")
                return None

            item = await self.menu_items.find_one({"_id": ObjectId(item_id)})
            if item:
                # Convert ObjectId to string
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])
                return MenuItemModel(**item)
            return None

        except Exception as e:
            logger.error(f"Error getting menu item by ID: {e}")
            return None

    async def get_menu_items_by_ids(self, item_ids: List[str]) -> List[MenuItemModel]:
        """Get multiple menu items by their IDs without filtering availability."""
        try:
            if self.menu_items is None or not item_ids:
                logger.warning("Menu items collection not available or no IDs provided")
                return []

            valid_ids = []
            for item_id in item_ids:
                if ObjectId.is_valid(item_id):
                    valid_ids.append(ObjectId(item_id))
                else:
                    logger.warning(f"Skipping invalid menu item ID: {item_id}")

            if not valid_ids:
                return []

            cursor = self.menu_items.find({"_id": {"$in": valid_ids}})
            items = await cursor.to_list(length=None)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting menu items by IDs: {e}")
            return []

    async def create_menu_item(
        self, item_data: dict, image_url: Optional[str] = None
    ) -> MenuItemModel:
        """Create a single menu item that can be available across multiple programs."""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            available_for_daily = bool(item_data.get("is_available_for_daily"))
            available_for_weekly = bool(item_data.get("is_available_for_meal_plan"))

            if not available_for_daily and not available_for_weekly:
                raise ValueError("At least one availability option must be selected")

            base_fields = {
                key: value
                for key, value in item_data.items()
                if key not in {"is_available_for_daily", "is_available_for_meal_plan"}
            }
            base_fields.setdefault("allergens", [])
            base_fields.setdefault("is_vegetarian", False)
            base_fields.setdefault("is_halal", True)

            now = datetime.utcnow()

            payload: Dict[str, Any] = {
                **base_fields,
                "is_available_for_daily": available_for_daily,
                "is_available_for_meal_plan": available_for_weekly,
                "is_available": base_fields.get("is_available", True),
                "created_at": now,
                "updated_at": now,
            }

            if "allergens" in payload:
                if isinstance(payload["allergens"], list):
                    payload["allergens"] = [
                        str(allergen).strip()
                        for allergen in payload["allergens"]
                        if str(allergen).strip()
                    ]
                else:
                    payload["allergens"] = []
            else:
                payload["allergens"] = []

            if image_url is not None:
                payload["image_url"] = image_url
            elif "image_url" not in payload:
                payload["image_url"] = None

            result = await self.menu_items.insert_one(payload)
            payload["_id"] = str(result.inserted_id)
            logger.info(
                "Menu item created: %s (ID: %s)",
                item_data.get("name"),
                result.inserted_id,
            )
            return MenuItemModel(**payload)

        except Exception as e:
            logger.error(f"Error creating menu item: {e}")
            raise

    async def update_menu_item(self, item_id: str, update_data: dict) -> Optional[MenuItemModel]:
        """Update existing menu item"""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                raise ValueError(f"Invalid item ID format: {item_id}")

            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            update_payload: Dict[str, Any] = {}
            for key, value in update_data.items():
                if value is None:
                    if key == "image_url":
                        update_payload[key] = None
                    continue
                update_payload[key] = value

            if not update_payload:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            result = await self.menu_items.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_payload}
            )

            if result.matched_count == 0:
                logger.warning(f"Menu item not found: {item_id}")
                return None

            # Get and return updated item
            item = await self.get_menu_item_by_id(item_id)
            logger.info(f"Menu item updated: {item_id}")
            return item

        except Exception as e:
            logger.error(f"Error updating menu item: {e}")
            raise

    async def delete_menu_item(self, item_id: str) -> bool:
        """Permanently delete a menu item."""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                logger.error(f"Invalid item ID format: {item_id}")
                return False

            result = await self.menu_items.delete_one({"_id": ObjectId(item_id)})

            success = result.deleted_count > 0
            if success:
                logger.info(f"Menu item permanently deleted: {item_id}")
            else:
                logger.warning(f"Menu item not found for deletion: {item_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting menu item: {e}")
            return False

    # ============= WEEKLY SCHEDULE METHODS =============

    async def create_weekly_menu_schedule(self, delivery_date: str, menu_rotation: int, menu_item_ids: List[str]) -> WeeklyMenuScheduleModel:
        """Create or update weekly menu schedule"""
        try:
            if self.weekly_schedule is None:
                raise ValueError("Weekly schedule collection not available")

            date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")

            # Validate menu items exist
            raw_ids: List[str] = []
            for item_id in menu_item_ids:
                value = str(item_id).strip()
                if not value:
                    continue
                if not ObjectId.is_valid(value):
                    logger.warning("Ignoring invalid menu item ID for weekly schedule: %s", value)
                    continue
                raw_ids.append(value)

            if not raw_ids:
                raise ValueError("No valid menu item IDs provided")

            # Deduplicate while preserving order
            item_object_ids: List[ObjectId] = []
            seen: Set[ObjectId] = set()
            for value in raw_ids:
                oid = ObjectId(value)
                if oid in seen:
                    continue
                seen.add(oid)
                item_object_ids.append(oid)

            # Check if items exist; drop missing ones instead of failing
            if self.menu_items is not None:
                existing_cursor = self.menu_items.find(
                    {"_id": {"$in": item_object_ids}},
                    projection={"_id": 1},
                )
                existing_docs = await existing_cursor.to_list(length=None)
                existing_ids = {doc["_id"] for doc in existing_docs}
                filtered_ids = [oid for oid in item_object_ids if oid in existing_ids]

                if not filtered_ids:
                    raise ValueError("None of the provided menu items exist")

                if len(filtered_ids) != len(item_object_ids):
                    logger.warning(
                        "Dropping %d missing menu items while creating weekly schedule for %s",
                        len(item_object_ids) - len(filtered_ids),
                        delivery_date,
                    )
                item_object_ids = filtered_ids

            # Create or update schedule (store ObjectIds in Mongo)
            schedule_dict = {
                "delivery_date": date_obj,
                "menu_rotation": menu_rotation,
                "menu_items": item_object_ids,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # Use upsert to create or update
            result = await self.weekly_schedule.update_one(
                {"delivery_date": date_obj},
                {"$set": schedule_dict},
                upsert=True
            )

            # Build a response payload with stringified IDs so Pydantic validation succeeds
            response_payload: Dict[str, Any] = {
                **schedule_dict,
                "menu_items": [str(item) for item in schedule_dict.get("menu_items", [])],
            }

            if result.upserted_id:
                response_payload["_id"] = str(result.upserted_id)
                logger.info(f"Weekly schedule created for {delivery_date}")
            else:
                existing = await self.weekly_schedule.find_one(
                    {"delivery_date": date_obj},
                    projection={"_id": 1},
                )
                if existing and existing.get("_id"):
                    response_payload["_id"] = str(existing["_id"])
                logger.info(f"Weekly schedule updated for {delivery_date}")

            return WeeklyMenuScheduleModel(**response_payload)

        except Exception as e:
            logger.error(f"Error creating weekly menu schedule: {e}")
            raise

    # ============= UTILITY METHODS =============

    async def get_categories(self) -> List[CategoryModel]:
        """Get all active food categories (public endpoint - alias for consistency)"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return []

            cursor = self.categories.find({"is_active": True}).sort("sort_order", 1)
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise

    async def search_menu_items(self, query: str, category: Optional[str] = None) -> List[MenuItemModel]:
        """Search menu items by name or description"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            # Build search query
            search_filter = {
                "is_available": True,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }

            if category:
                search_filter["category"] = category

            cursor = self.menu_items.find(search_filter).sort("name", 1).limit(20)
            items = await cursor.to_list(length=20)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error searching menu items: {e}")
            return []

# Create service instance (singleton)
menu_service = MenuService()
