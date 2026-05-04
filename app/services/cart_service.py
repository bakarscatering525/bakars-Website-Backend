from typing import Dict, List
from bson import ObjectId
from app.config.database import get_database
from app.services.menu_service import menu_service
import logging

logger = logging.getLogger(__name__)


class CartService:
    def __init__(self):
        self._db = None
        self._carts = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def carts(self):
        if self._carts is None and self.db is not None:
            self._carts = self.db.carts
        return self._carts

    async def get_cart(self, user_id: str) -> Dict:
        """Fetch or create a user's cart."""
        if self.carts is None:
            raise ValueError("Carts collection not available")

        cart = await self.carts.find_one({"user_id": ObjectId(user_id)})
        if not cart:
            cart = {
                "user_id": ObjectId(user_id),
                "items": [],
            }
            result = await self.carts.insert_one(cart)
            cart["_id"] = result.inserted_id
        return cart

    async def add_to_cart(self, user_id: str, item_id: str, quantity: int) -> Dict:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        cart = await self.get_cart(user_id)

        # Ensure menu item exists
        menu_item = await menu_service.get_menu_item_by_id(item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        existing_item = next(
            (item for item in cart["items"] if item["item_id"] == item_id),
            None,
        )

        if existing_item:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id), "items.item_id": item_id},
                {"$inc": {"items.$.quantity": quantity}},
            )
        else:
            cart_item = {
                "item_id": item_id,
                "item_name": menu_item.name,
                "category": menu_item.category,
                "price": menu_item.price,
                "quantity": quantity,
            }
            await self.carts.update_one(
                {"user_id": ObjectId(user_id)},
                {"$push": {"items": cart_item}},
            )

        return await self.get_cart_summary(user_id)

    async def update_cart_item(self, user_id: str, item_id: str, quantity: int) -> Dict:
        if self.carts is None:
            raise ValueError("Carts collection not available")

        if quantity <= 0:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id)},
                {"$pull": {"items": {"item_id": item_id}}},
            )
        else:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id), "items.item_id": item_id},
                {"$set": {"items.$.quantity": quantity}},
            )

        return await self.get_cart_summary(user_id)

    async def remove_from_cart(self, user_id: str, item_id: str) -> Dict:
        if self.carts is None:
            raise ValueError("Carts collection not available")

        await self.carts.update_one(
            {"user_id": ObjectId(user_id)},
            {"$pull": {"items": {"item_id": item_id}}},
        )
        return await self.get_cart_summary(user_id)

    async def get_cart_summary(self, user_id: str) -> Dict:
        cart = await self.get_cart(user_id)
        items: List[Dict] = []
        subtotal = 0.0

        for item in cart.get("items", []):
            item_subtotal = item["price"] * item["quantity"]
            items.append(
                {
                    "item_id": item["item_id"],
                    "item_name": item["item_name"],
                    "category": item.get("category", ""),
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "subtotal": item_subtotal,
                }
            )
            subtotal += item_subtotal

        return {
            "items": items,
            "subtotal": subtotal,
            "items_count": len(items),
            "delivery_fee": 0.0,
            "total": subtotal,
        }

    async def clear_cart(self, user_id: str) -> bool:
        if self.carts is None:
            logger.warning("Carts collection not available")
            return False

        await self.carts.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"items": []}},
        )
        logger.info(f"Cart cleared for user {user_id}")
        return True


cart_service = CartService()
