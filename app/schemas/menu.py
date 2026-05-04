from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryResponse(BaseModel):
    """Category response"""
    id: str
    _id: str
    name: str
    display_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    sort_order: int

    @classmethod
    def from_model(cls, category):
        """Convert CategoryModel to CategoryResponse"""
        return cls(
            id=str(category.id),
            _id=str(category.id),
            name=category.name,
            display_name=category.display_name,
            description=category.description,
            image_url=category.image_url,
            is_active=category.is_active,
            sort_order=category.sort_order
        )

class MenuItemResponse(BaseModel):
    """Menu item response"""
    id: str
    _id: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    image_url: Optional[str] = None
    is_available: bool
    is_available_for_daily: bool
    is_available_for_meal_plan: bool
    allergens: List[str] = []
    spice_level: Optional[str] = None
    is_vegetarian: bool
    is_vegan: bool = False
    is_halal: bool
    nutritional_info: Optional[dict] = None
    serving_size: Optional[str] = None
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, item):
        """Convert MenuItemModel to MenuItemResponse"""
        created_at_str = item.created_at.isoformat() if isinstance(item.created_at, datetime) else str(item.created_at)
        updated_at_str = item.updated_at.isoformat() if isinstance(item.updated_at, datetime) else str(item.updated_at)
        
        return cls(
            id=str(item.id),
            _id=str(item.id),
            name=item.name,
            description=item.description,
            category=item.category,
            price=item.price,
            image_url=item.image_url,
            is_available=item.is_available,
            is_available_for_daily=item.is_available_for_daily,
            is_available_for_meal_plan=item.is_available_for_meal_plan,
            allergens=item.allergens or [],
            spice_level=item.spice_level,
            is_vegetarian=item.is_vegetarian,
            is_vegan=getattr(item, 'is_vegan', False),
            is_halal=item.is_halal,
            nutritional_info=getattr(item, 'nutritional_info', None),
            serving_size=getattr(item, 'serving_size', None),
            created_at=created_at_str,
            updated_at=updated_at_str
        )

class CateringPackageResponse(BaseModel):
    """Catering package response"""
    id: str
    name: str
    display_name: str
    price_per_head: float
    description: str
    rules: dict

class PaginationMeta(BaseModel):
    """Generic pagination metadata"""
    page: int
    page_size: int
    total_items: int
    total_pages: int

class WeeklyMenuResponse(BaseModel):
    """Weekly menu response"""
    delivery_date: str
    menu_rotation: int
    items: List[MenuItemResponse]
    pagination: Optional[PaginationMeta] = None

class PaginatedMenuItemsResponse(BaseModel):
    """Daily menu response with pagination details"""
    items: List[MenuItemResponse]
    pagination: PaginationMeta

class DailyMenuAvailabilityResponse(BaseModel):
    """Daily menu ordering window details"""
    is_open: bool
    window_label: str
    timezone: str
    opens_at: str
    closes_at: str
    current_time: str
    message: str

# Request models
class CreateMenuItemRequest(BaseModel):
    """Create menu item request"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    is_available_for_daily: bool = True
    is_available_for_meal_plan: bool = False
    allergens: List[str] = []
    spice_level: Optional[str] = Field(None, pattern="^(mild|medium|hot)$")
    is_vegetarian: bool = False
    is_halal: bool = True

class UpdateMenuItemRequest(BaseModel):
    """Update menu item request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_available_for_daily: Optional[bool] = None
    is_available_for_meal_plan: Optional[bool] = None
    allergens: Optional[List[str]] = None
    spice_level: Optional[str] = Field(None, pattern="^(mild|medium|hot)$")
    is_vegetarian: Optional[bool] = None
    is_halal: Optional[bool] = None
