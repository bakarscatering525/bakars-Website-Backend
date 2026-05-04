from pydantic import BaseModel
from typing import Optional

class CreatePaymentIntentRequest(BaseModel):
    """Create payment intent request"""
    order_id: str

class CreatePaymentIntentResponse(BaseModel):
    """Create payment intent response"""
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str

class ConfirmPaymentRequest(BaseModel):
    """Confirm payment request"""
    payment_intent_id: str

class ConfirmPaymentResponse(BaseModel):
    """Confirm payment response"""
    success: bool
    order_id: str
    payment_status: str
    message: str

class RefundRequest(BaseModel):
    """Refund request"""
    order_id: str
    amount: Optional[float] = None  # If None, full refund
    reason: Optional[str] = None

class PaymentConfigResponse(BaseModel):
    """Stripe publishable key + status"""
    stripe_enabled: bool
    stripe_publishable_key: Optional[str] = None
    currency: str
    is_live_mode: bool = False
