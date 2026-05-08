from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    """Cart item"""
    item_id: str
    item_name: str
    category: str
    quantity: int
    price: float
    subtotal: float
    variation_size: Optional[str] = None

class CartSummary(BaseModel):
    """Cart summary"""
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    items_count: int

class AddToCartRequest(BaseModel):
    """Add to cart request"""
    item_id: str
    quantity: int = 1
    variation_size: Optional[str] = None

class UpdateCartItemRequest(BaseModel):
    """Update cart item request"""
    quantity: int
    variation_size: Optional[str] = None
