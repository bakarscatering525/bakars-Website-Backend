from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class CateringOrderModel(BaseModel):
    """Catering order-specific data"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: PyObjectId  # Reference to main order
    user_id: PyObjectId
    
    # Event details
    event_date: datetime
    event_time: Optional[str] = None
    venue_address: str
    guest_count: int
    
    # Package details
    package_type: str  # basic, premium, diamond
    package_price_per_head: float
    
    # Selected items
    selected_items: Dict[str, List[str]] = {}  # {category: [item_ids]}
    
    # Pricing
    package_total: float
    delivery_fee: float
    advance_payment_amount: float
    remaining_payment_amount: float
    
    # Payment tracking
    advance_paid: bool = False
    advance_payment_date: Optional[datetime] = None
    final_paid: bool = False
    final_payment_date: Optional[datetime] = None
    
    # Quote
    quote_sent: bool = False
    quote_sent_at: Optional[datetime] = None
    quote_accepted: bool = False
    
    # Additional details
    special_requests: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
