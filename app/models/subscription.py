from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class WeekSelectionRulesModel(BaseModel):
    """Rules describing how many weeks a customer can schedule within a cycle."""

    available_weeks: Optional[int] = Field(default=None, ge=1)
    required_weeks: Optional[int] = Field(default=None, ge=1)
    deliveries_per_week: Optional[int] = Field(default=None, ge=1)
    allow_partial_weeks: bool = False


class CustomerNotificationSettingsModel(BaseModel):
    """Optional messaging displayed to customers for a plan."""

    upsell_message: Optional[str] = None
    reminder_message: Optional[str] = None
    upsell_condition: str = "always"


class ReminderSettingsModel(BaseModel):
    """Reminder scheduling configuration for subscribers."""

    enabled: bool = False
    frequency_days: int = Field(default=7, ge=1)
    channel: str = "in_app"  # in_app, email, both
    threshold_unselected_boxes: Optional[int] = Field(default=None, ge=0)


class MealSubscriptionPlanModel(BaseModel):
    """Configurable meal subscription plan definition."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    code: str
    name: str
    tab: str  # regular, weekly, fortnight, monthly, custom
    description: Optional[str] = None
    short_description: Optional[str] = None
    included_meals: int = 0
    deliveries_per_cycle: int = 0
    weeks_in_cycle: int = 0
    boxes_per_delivery: int = 0
    max_boxes_per_meal: Optional[int] = None
    price_per_plan: float = 0.0
    price_per_box: Optional[float] = None
    allow_multiple: bool = True
    min_boxes_delivery: Optional[int] = None
    min_boxes_pickup: Optional[int] = None
    display_badge: Optional[str] = None
    display_order: int = 0
    extra_box_price: Optional[float] = None
    highlight: bool = False
    is_active: bool = True
    require_terms_ack: bool = False
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRulesModel] = None
    customer_notifications: Optional[CustomerNotificationSettingsModel] = None
    reminder_settings: Optional[ReminderSettingsModel] = None
    metadata: Optional[Dict[str, Any]] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    menu_item_ids_by_day: Dict[str, List[str]] = Field(default_factory=dict)
    menu_items_by_day: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    menu_item_ids_by_delivery_date: Dict[str, List[str]] = Field(default_factory=dict)
    menu_items_by_delivery_date: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MealPlanSelection(BaseModel):
    """Selected plan information stored with an order."""

    plan_id: str
    plan_code: str
    plan_name: str
    plan_tab: str
    quantity: int
    included_meals: int
    included_boxes: int
    deliveries_in_cycle: int
    weeks_in_cycle: int
    max_boxes_per_meal: Optional[int] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRulesModel] = None
    customer_notifications: Optional[CustomerNotificationSettingsModel] = None
    metadata: Optional[Dict[str, Any]] = None
    plan_price: float = 0.0
    discount_applied: float = 0.0


class DeliverySlotSelection(BaseModel):
    """Meal selections for a specific delivery date."""

    delivery_date: datetime
    menu_items: Dict[str, int]  # {menu_item_id: quantity}
    notes: Optional[str] = None
    cutoff_at: Optional[datetime] = None
    locked_at: Optional[datetime] = None
    locked_by: Optional[str] = None


class MealSubscriptionModel(BaseModel):
    """Stored meal subscription order data."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: PyObjectId
    user_id: PyObjectId

    fulfilment_type: str  # delivery, pickup, mixed
    postal_code: Optional[str] = None
    plan_selections: List[MealPlanSelection] = []
    delivery_slots: List[DeliverySlotSelection] = []

    total_selected_boxes: int = 0
    total_included_boxes: int = 0
    extra_boxes: int = 0
    extra_boxes_price: float = 0.0

    delivery_days: int = 0
    delivery_fee_per_day: float = 0.0
    total_delivery_fee: float = 0.0
    express_delivery: bool = False
    delivery_fee_notes: Optional[str] = None

    reminder_settings: Optional[ReminderSettingsModel] = None
    next_reminder_at: Optional[datetime] = None
    reminders_sent: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
