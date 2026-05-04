from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class DeliveryZoneModel(BaseModel):
    """Delivery zone definition with postcode based pricing."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    zone_label: Optional[str] = None  # e.g. Zone 1 (0-14 km)
    postcode: str
    suburbs: List[str] = Field(default_factory=list)
    state: str = "NSW"
    distance_from_business: Optional[float] = None  # in km
    base_delivery_fee: float = 10.0  # per delivery day
    express_delivery_fee: Optional[float] = None  # optional surcharge per day
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    order_types: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
