from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.auth import AddressSchema
from app.models.order import OrderItem  # Import OrderItem from models
from app.schemas.subscription import PlanSelectionPayload, DeliverySlotPayload

class DailyOrderItemPayload(BaseModel):
    """Daily menu item payload."""
    item_id: str = Field(..., description="Menu item identifier")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class CreateDailyOrderRequest(BaseModel):
    """Create daily order request"""
    items: List[DailyOrderItemPayload]
    delivery_method: str  # standard, pickup
    delivery_address_id: Optional[str] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    payment_method: str = "cash"

class CreateMealSubscriptionOrderRequest(BaseModel):
    """Create meal subscription order request"""
    plan_selections: List[PlanSelectionPayload]
    delivery_slots: List[DeliverySlotPayload]
    sidelines: Optional[List[DailyOrderItemPayload]] = None
    delivery_address_id: Optional[str] = None
    fulfilment_method: str = "delivery"  # delivery, pickup
    is_express: bool = False
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    payment_method: str = "cash"

    @validator("plan_selections")
    def validate_plans(cls, value: List[PlanSelectionPayload]) -> List[PlanSelectionPayload]:
        if not value:
            raise ValueError("At least one meal plan selection is required")
        return value

    @validator("delivery_slots")
    def validate_slots(cls, value: List[DeliverySlotPayload]) -> List[DeliverySlotPayload]:
        if not value:
            raise ValueError("Delivery slots are required")
        return value

class CreateCateringOrderRequest(BaseModel):
    """Create catering order request"""
    package_type: str  # basic, premium, diamond
    guest_count: int
    event_date: str  # YYYY-MM-DD
    event_time: Optional[str] = None
    venue_address: str
    selected_items: Dict[str, List[str]]  # {category: [item_ids]}
    special_requests: Optional[str] = None
    payment_method: str = "cash"
    
    @validator('guest_count')
    def validate_guest_count(cls, v):
        if v < 10:
            raise ValueError('Minimum 10 guests required for catering')
        return v

class UpdateMealSubscriptionOrderRequest(CreateMealSubscriptionOrderRequest):
    """Update meal subscription order request"""
    pass


class UpdateDeliverySlotMenuItemsRequest(BaseModel):
    """Update menu items for a specific delivery date on a meal subscription."""

    delivery_date: str
    menu_items: Dict[str, int]
    notes: Optional[str] = None
    override_cutoff: bool = False

    @validator("delivery_date")
    def validate_delivery_date(cls, value: str) -> str:
        if not value:
            raise ValueError("delivery_date is required")
        return value

    @validator("menu_items")
    def validate_menu_items(cls, value: Dict[str, int]) -> Dict[str, int]:
        if not value:
            raise ValueError("menu_items must include at least one item")
        cleaned: Dict[str, int] = {}
        for key, qty in value.items():
            try:
                int_qty = int(qty)
            except (TypeError, ValueError):
                int_qty = 0
            if int_qty <= 0:
                continue
            cleaned[str(key)] = int_qty
        if not cleaned:
            raise ValueError("menu_items must include at least one valid item with quantity")
        return cleaned


class OrderResponse(BaseModel):
    """Order response"""
    id: str
    order_number: str
    order_type: str
    status: str
    payment_status: str
    items: List[OrderItem]
    sidelines: Optional[List[OrderItem]] = None
    subtotal: float
    tax_amount: Optional[float] = 0.0
    delivery_fee: float
    total_amount: float
    delivery_method: str
    delivery_address_id: Optional[str] = None
    delivery_address: Optional[AddressSchema] = None
    created_at: str
    payment_intent_id: Optional[str] = None
    payment_method: Optional[str] = None
    primary_plan_tab: Optional[str] = None
    primary_plan_name: Optional[str] = None
    extra_boxes: Optional[int] = 0
    extra_boxes_price: Optional[float] = 0.0
    plan_price_total: Optional[float] = 0.0

class OrderListResponse(BaseModel):
    """Order list response"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int

class UpdateOrderStatusRequest(BaseModel):
    """Update order status request"""
    status: str  # confirmed, preparing, out_for_delivery, delivered, cancelled
    admin_notes: Optional[str] = None
