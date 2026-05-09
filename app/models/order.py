from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class OrderItem(BaseModel):
    """Order item"""
    item_id: str
    item_name: str
    category: str
    quantity: int
    price: float
    subtotal: float

class OrderModel(BaseModel):
    """Main order model"""
    id: Optional[str] = Field(default=None, alias="_id")
    order_number: str
    user_id: str  # Changed from PyObjectId to str
    order_type: str  # daily, weekly, catering
    status: str = "pending"  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    payment_status: str = "pending"  # pending, paid, failed, refunded, partially_paid
    
    # Order items
    items: List[OrderItem] = []
    sidelines: List[OrderItem] = []
    
    # Pricing
    subtotal: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    delivery_fee: float
    total_amount: float

    # Delivery details
    delivery_method: str  # standard, express, pickup
    delivery_address_id: Optional[str] = None
    delivery_address: Optional[dict] = None
    delivery_instructions: Optional[str] = None
    
    # Payment details
    stripe_payment_intent_id: Optional[str] = None
    payment_method: Optional[str] = None
    paid_amount: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    
    # Additional metadata
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    primary_plan_tab: Optional[str] = None
    primary_plan_name: Optional[str] = None
    extra_boxes: int = 0
    extra_boxes_price: float = 0.0
    plan_price_total: float = 0.0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
