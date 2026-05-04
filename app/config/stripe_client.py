import stripe
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Configure Stripe only if key is available
active_secret = settings.active_stripe_secret_key
if active_secret:
    stripe.api_key = active_secret
    mode_label = "test" if settings.STRIPE_TEST_MODE else "live"
    logger.info("Stripe client configured (%s mode)", mode_label)
else:
    logger.warning("Stripe API key not configured - payment processing will not work")

class StripeClient:
    @staticmethod
    async def create_payment_intent(
        amount: float,
        currency: str,
        metadata: dict,
        description: str = None
    ):
        """Create a Stripe Payment Intent"""
        if not settings.active_stripe_secret_key:
            logger.error("Stripe not configured")
            raise Exception("Payment processing not configured")
        
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata,
                description=description,
                payment_method_types=["card"],
            )
            
            logger.info(f"Payment intent created: {payment_intent.id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise Exception(f"Payment processing error: {str(e)}")

    @staticmethod
    async def confirm_payment(payment_intent_id: str):
        """Retrieve and verify payment intent status"""
        if not settings.active_stripe_secret_key:
            logger.error("Stripe not configured")
            raise Exception("Payment processing not configured")
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Error confirming payment: {e}")
            raise Exception(f"Payment confirmation error: {str(e)}")

    @staticmethod
    async def create_refund(payment_intent_id: str, amount: float = None):
        """Create a refund for a payment intent"""
        if not settings.active_stripe_secret_key:
            logger.error("Stripe not configured")
            raise Exception("Payment processing not configured")
        
        try:
            refund_data = {
                'payment_intent': payment_intent_id
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            logger.info(f"Refund created: {refund.id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Refund error: {e}")
            raise Exception(f"Refund processing error: {str(e)}")

    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str):
        """Verify Stripe webhook signature"""
        active_secret = settings.active_stripe_secret_key
        active_webhook = settings.active_stripe_webhook_secret
        if not active_secret or not active_webhook:
            logger.error("Stripe not fully configured")
            raise Exception("Webhook processing not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, active_webhook
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise Exception("Invalid signature")

stripe_client = StripeClient()
