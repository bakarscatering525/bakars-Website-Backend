from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

class CategoryModel(BaseModel):
    """Food category model"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str  # rice, curry, bbq, sweets, drinks
    display_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MenuItemModel(BaseModel):
    """Menu item model"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    category: str  # rice, curry, bbq, sweets, drinks
    price: float
    variations: List[Dict] = []  # Size variations: [{size: "small", price: 10.99, is_available: true}, ...]
    image_url: Optional[str] = None
    is_available: bool = True
    is_available_for_daily: bool = True
    is_available_for_meal_plan: bool = False
    allergens: List[str] = []
    spice_level: Optional[str] = None  # mild, medium, hot
    is_vegetarian: bool = False
    is_vegan: bool = False  # ✅ ADD THIS FIELD
    is_halal: bool = True
    nutritional_info: Optional[Dict] = None  # ✅ ADD THIS FIELD
    serving_size: Optional[str] = None  # ✅ ADD THIS FIELD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class WeeklyMenuScheduleModel(BaseModel):
    """Weekly menu rotation schedule"""
    id: Optional[str] = Field(default=None, alias="_id")
    delivery_date: datetime  # Monday or Thursday
    menu_rotation: int  # 1-8 (8 rotations per month)
    menu_items: List[str] = []  # List of menu item IDs
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CateringPackageModel(BaseModel):
    """Catering package definition"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str  # basic, premium, diamond
    display_name: str
    price_per_head: float
    description: str
    rules: dict  # Package composition rules
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
