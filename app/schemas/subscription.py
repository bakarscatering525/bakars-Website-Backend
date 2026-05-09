from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator, model_validator

from app.schemas.menu import MenuItemResponse

VALID_DELIVERY_DAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


class WeekSelectionRules(BaseModel):
    available_weeks: Optional[int] = Field(default=None, ge=1, le=12)
    required_weeks: Optional[int] = Field(default=None, ge=1, le=12)
    deliveries_per_week: Optional[int] = Field(default=None, ge=1, le=14)
    allow_partial_weeks: bool = False

    @model_validator(mode="after")
    def validate_week_window(cls, values: "WeekSelectionRules") -> "WeekSelectionRules":
        available = values.available_weeks
        required = values.required_weeks
        if available is not None and required is not None and required > available:
            raise ValueError(
                "required_weeks cannot be greater than available_weeks"
            )
        return values


class CustomerNotificationSettings(BaseModel):
    upsell_message: Optional[str] = None
    reminder_message: Optional[str] = None
    upsell_condition: Optional[str] = Field(
        default="always", description="always, when_plan_selected, when_no_plan, hidden"
    )

    @validator("upsell_condition", pre=True, always=True)
    def normalize_condition(cls, value: Optional[str]) -> str:
        default_value = "always"
        if not value:
            return default_value
        normalized = value.strip().lower()
        allowed = {"always", "when_plan_selected", "when_no_plan", "hidden"}
        if normalized not in allowed:
            return default_value
        return normalized


class ReminderSettings(BaseModel):
    enabled: bool = False
    frequency_days: int = Field(default=7, ge=1, le=30)
    channel: str = Field(default="in_app")  # in_app, email, both
    threshold_unselected_boxes: Optional[int] = Field(default=None, ge=0)


class MealSubscriptionPlanBase(BaseModel):
    code: str
    name: str
    tab: str
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
    require_terms_ack: bool = False
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRules] = None
    customer_notifications: Optional[CustomerNotificationSettings] = None
    reminder_settings: Optional[ReminderSettings] = None
    metadata: Optional[Dict[str, Any]] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    menu_item_ids_by_day: Dict[str, List[str]] = Field(default_factory=dict)
    menu_item_ids_by_delivery_date: Dict[str, List[str]] = Field(default_factory=dict)

    @validator("code")
    def normalize_code(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    @validator("tab")
    def normalize_tab(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed_tabs = {
            "regular",
            "weekly",
            "fortnight",
            "monthly",
            "custom",
        }
        if normalized not in allowed_tabs:
            raise ValueError(
                f"Invalid tab '{value}'. Must be one of: {', '.join(sorted(allowed_tabs))}"
            )
        return normalized

    @validator("available_delivery_days", each_item=True, pre=True)
    def normalize_available_days(cls, value: str) -> str:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in VALID_DELIVERY_DAYS:
            raise ValueError(f"Invalid delivery day: {value}")
        return normalized

    @validator("menu_item_ids_by_day", pre=True, always=True)
    def normalize_menu_day_mapping(
        cls, value: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        if value is None:
            return {}
        normalized: Dict[str, List[str]] = {}
        for raw_day, items in value.items():
            if raw_day is None:
                continue
            day = str(raw_day).strip().lower()
            if day not in VALID_DELIVERY_DAYS:
                raise ValueError(
                    f"Invalid delivery day provided for menu mapping: {raw_day}"
                )
            if items is None:
                normalized[day] = []
                continue
            if not isinstance(items, list):
                raise ValueError("Menu items mapping must be a list of item IDs")
            normalized[day] = [str(item_id) for item_id in items if item_id is not None]
        return normalized

    @validator("menu_item_ids_by_delivery_date", pre=True, always=True)
    def normalize_menu_date_mapping(
        cls, value: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        if value is None:
            return {}
        normalized: Dict[str, List[str]] = {}
        for raw_date, items in value.items():
            if raw_date is None:
                continue
            date_str = str(raw_date).strip()
            try:
                parsed = datetime.fromisoformat(date_str)
            except Exception:
                raise ValueError(f"Invalid delivery date format: {raw_date}. Use YYYY-MM-DD")
            weekday = parsed.weekday()
            if weekday not in (0, 3):  # Monday or Thursday
                raise ValueError("Delivery dates must be on Monday or Thursday")
            clean_items: List[str] = []
            if items is None:
                normalized[date_str] = []
                continue
            if not isinstance(items, list):
                raise ValueError("Menu items mapping must be a list of item IDs")
            for item_id in items:
                if item_id is None:
                    continue
                clean_items.append(str(item_id))
            normalized[date_str] = clean_items
        return normalized

    @validator("terms_and_conditions", each_item=True, pre=True)
    def normalize_terms(cls, value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = value.strip()
        return normalized


class CreateMealSubscriptionPlanRequest(MealSubscriptionPlanBase):
    is_active: bool = True


class UpdateMealSubscriptionPlanRequest(BaseModel):
    name: Optional[str] = None
    tab: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    included_meals: Optional[int] = None
    deliveries_per_cycle: Optional[int] = None
    weeks_in_cycle: Optional[int] = None
    boxes_per_delivery: Optional[int] = None
    max_boxes_per_meal: Optional[int] = None
    price_per_plan: Optional[float] = None
    price_per_box: Optional[float] = None
    allow_multiple: Optional[bool] = None
    min_boxes_delivery: Optional[int] = None
    min_boxes_pickup: Optional[int] = None
    display_badge: Optional[str] = None
    display_order: Optional[int] = None
    extra_box_price: Optional[float] = None
    highlight: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    require_terms_ack: Optional[bool] = None
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: Optional[List[str]] = None
    week_selection_rules: Optional[WeekSelectionRules] = None
    customer_notifications: Optional[CustomerNotificationSettings] = None
    reminder_settings: Optional[ReminderSettings] = None
    menu_item_ids_by_delivery_date: Optional[Dict[str, List[str]]] = None


class MealSubscriptionPlanResponse(MealSubscriptionPlanBase):
    id: str = Field(alias="_id")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    menu_items_by_day: Dict[str, List[MenuItemResponse]] = Field(default_factory=dict)
    menu_items_by_delivery_date: Dict[str, List[MenuItemResponse]] = Field(default_factory=dict)


class MealSubscriptionPlanGroupedResponse(BaseModel):
    tab: str
    plans: List[MealSubscriptionPlanResponse]


class DeliveryZoneBase(BaseModel):
    postcode: str
    zone_label: Optional[str] = None
    suburbs: List[str] = Field(default_factory=list)
    state: str = "NSW"
    distance_from_business: Optional[float] = None
    base_delivery_fee: float = 10.0
    express_delivery_fee: Optional[float] = None
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True
    order_types: List[str] = Field(default_factory=list)


class CreateDeliveryZoneRequest(DeliveryZoneBase):
    pass


class UpdateDeliveryZoneRequest(BaseModel):
    zone_label: Optional[str] = None
    suburbs: Optional[List[str]] = None
    state: Optional[str] = None
    distance_from_business: Optional[float] = None
    base_delivery_fee: Optional[float] = None
    express_delivery_fee: Optional[float] = None
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    order_types: Optional[List[str]] = None


class DeliveryZoneResponse(DeliveryZoneBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

class MealPlanListResponse(BaseModel):
    plans: List[MealSubscriptionPlanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanSelectionPayload(BaseModel):
    plan_id: str
    quantity: int = Field(ge=1)


class DeliverySlotPayload(BaseModel):
    delivery_date: str  # ISO date
    menu_items: Dict[str, int]
    variation_sizes: Optional[Dict[str, str]] = None
    fulfilment_method: Optional[str] = None  # delivery|pickup
    notes: Optional[str] = None

    @validator("delivery_date")
    def validate_delivery_date(cls, value: str) -> str:
        if not value:
            raise ValueError("delivery_date is required")
        return value

    @validator("menu_items")
    def validate_menu_items(cls, value: Dict[str, int]) -> Dict[str, int]:
        if not value:
            raise ValueError("menu_items must include at least one item")
        return value

    @validator("variation_sizes", pre=True)
    def normalize_variation_sizes(
        cls, value: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("variation_sizes must be a mapping of item IDs to variation size")
        normalized: Dict[str, str] = {}
        allowed = {"small", "medium", "large"}
        for raw_id, raw_size in value.items():
            if raw_id is None:
                continue
            item_id = str(raw_id).strip()
            if not item_id:
                continue
            size = str(raw_size).strip().lower() if raw_size is not None else ""
            if not size:
                continue
            if size not in allowed:
                raise ValueError(f"Invalid variation size '{raw_size}'. Must be one of: small, medium, large")
            normalized[item_id] = size
        return normalized or None

    @validator("fulfilment_method", pre=True)
    def normalize_fulfilment_method(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        if normalized not in {"delivery", "pickup"}:
            raise ValueError("fulfilment_method must be 'delivery' or 'pickup'")
        return normalized
