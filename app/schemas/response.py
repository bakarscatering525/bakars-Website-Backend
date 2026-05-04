from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

class DeliveryCheckResponse(BaseModel):
    """Delivery availability check response"""
    available: bool
    distance_km: Optional[float] = None
    delivery_fee: Optional[float] = None
    suburb: Optional[str] = None
    postcode: Optional[str] = None
    message: Optional[str] = None

class RevenueDaySummary(BaseModel):
    label: str
    date: str
    total: float


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_orders: int = 0
    total_orders_growth_percent: float = 0.0
    pending_orders: int = 0
    pending_orders_weekly_change_percent: float = 0.0
    confirmed_orders: int = 0
    preparing_orders: int = 0
    out_for_delivery_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    today_revenue: float = 0.0
    today_vs_yesterday_percent: float = 0.0
    weekly_revenue: float = 0.0
    weekly_growth_percent: float = 0.0
    monthly_revenue: float = 0.0
    monthly_growth_percent: float = 0.0
    total_revenue: float = 0.0
    total_revenue_growth_percent: float = 0.0
    weekly_revenue_breakdown: list[RevenueDaySummary] = []
    active_subscriptions: int = 0
    upcoming_catering_events: int = 0
