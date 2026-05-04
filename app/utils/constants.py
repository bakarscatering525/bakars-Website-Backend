from enum import Enum

class OrderType(str, Enum):
    DAILY = "daily"
    MEAL_SUBSCRIPTION = "meal_subscription"
    CATERING = "catering"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_PAID = "partially_paid"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class FoodCategory(str, Enum):
    RICE = "rice"
    CURRY = "curry"
    BBQ = "bbq"
    SWEETS = "sweets"
    DRINKS = "drinks"

class CateringPackage(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    DIAMOND = "diamond"

class DeliveryMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    PICKUP = "pickup"

# Daily Menu Delivery Defaults
DAILY_DELIVERY_FEE = 12.0
DAILY_DELIVERY_RADIUS = 6.0  # km from Guildford

# Meal Subscription Tabs
MEAL_PLAN_TAB_REGULAR = "regular"
MEAL_PLAN_TAB_WEEKLY = "weekly"
MEAL_PLAN_TAB_FORTNIGHT = "fortnight"
MEAL_PLAN_TAB_MONTHLY = "monthly"

# Meal Subscription Defaults
REGULAR_DELIVERY_MIN_BOXES = 4
REGULAR_PICKUP_MIN_BOXES = 1
DEFAULT_MEAL_PLAN_MAX_BOXES_PER_MEAL = 2
DEFAULT_EXTRA_BOX_PRICE = 12.0
DEFAULT_EXPRESS_FEE_PER_DAY = 10.0

LEGACY_DEFAULT_PLAN_CODES = [
    "regular_flex",
    "weekly_10_meal",
    "fortnight_duo",
    "monthly_builder",
]

# Catering Constants
CATERING_BASIC_PRICE = 25.0
CATERING_PREMIUM_PRICE = 35.0
CATERING_DIAMOND_PRICE = 50.0
CATERING_ADVANCE_PAYMENT_PERCENT = 0.5
CATERING_BASE_DELIVERY_FEE = 30.0

# Order Number Format
ORDER_NUMBER_PREFIX = "BF"
