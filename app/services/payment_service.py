from typing import Optional
from app.config.stripe_client import stripe_client
from app.services.order_service import order_service
from app.utils.constants import PaymentStatus
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    async def create_payment_intent(self, order_id: str) -> dict:
        """Create Stripe Payment Intent for order"""
        try:
            order = await order_service.get_order_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            if order.payment_status == PaymentStatus.PAID:
                raise ValueError("Order already paid")
            
            # Create payment intent
            payment_intent = await stripe_client.create_payment_intent(
                amount=order.total_amount,
                currency="aud",
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "user_id": str(order.user_id),
                    "order_type": order.order_type
                },
                description=f"Bakar's Food - Order {order.order_number}"
            )
            
            # Update order with payment intent ID
            await order_service.update_payment_status(
                order_id,
                PaymentStatus.PENDING,
                payment_intent.id
            )
            
            logger.info(f"Payment intent created for order {order.order_number}")
            
            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": order.total_amount,
                "currency": "AUD"
            }
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    async def confirm_payment(self, payment_intent_id: str) -> dict:
        """Confirm payment status"""
        try:
            payment_intent = await stripe_client.confirm_payment(payment_intent_id)
            
            order_id = payment_intent.metadata.get("order_id")
            
            if payment_intent.status == "succeeded":
                await order_service.update_payment_status(
                    order_id,
                    PaymentStatus.PAID,
                    payment_intent_id
                )
                
                logger.info(f"Payment confirmed for order {order_id}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "payment_status": "paid",
                    "message": "Payment successful"
                }
            else:
                await order_service.update_payment_status(
                    order_id,
                    PaymentStatus.FAILED
                )
                
                return {
                    "success": False,
                    "order_id": order_id,
                    "payment_status": "failed",
                    "message": "Payment failed"
                }
                
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            raise
    
    async def process_refund(self, order_id: str, amount: Optional[float] = None, reason: str = None) -> dict:
        """Process refund for order"""
        try:
            order = await order_service.get_order_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            if not order.stripe_payment_intent_id:
                raise ValueError("No payment intent found for this order")
            
            # Create refund
            refund = await stripe_client.create_refund(
                order.stripe_payment_intent_id,
                amount
            )
            
            # Update order status
            await order_service.update_payment_status(
                order_id,
                PaymentStatus.REFUNDED
            )
            
            logger.info(f"Refund processed for order {order.order_number}")
            
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": amount or order.total_amount,
                "message": "Refund processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            raise

payment_service = PaymentService()
