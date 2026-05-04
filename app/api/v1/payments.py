from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from app.schemas.payment import (
    CreatePaymentIntentRequest, CreatePaymentIntentResponse,
    ConfirmPaymentRequest, ConfirmPaymentResponse, RefundRequest,
    PaymentConfigResponse
)
from app.schemas.response import ApiResponse
from app.services.payment_service import payment_service
from app.services.order_service import order_service
from app.services.notification_service import notification_service
from app.config.stripe_client import stripe_client
from app.config.settings import settings
from app.middleware.auth_middleware import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/config", response_model=ApiResponse[PaymentConfigResponse], include_in_schema=False)
async def get_payment_config():
    """Expose publishable Stripe config for the frontend."""
    publishable_key = settings.active_stripe_publishable_key
    stripe_enabled = bool(publishable_key)
    is_live_mode = settings.is_live_stripe_mode

    return ApiResponse(
        success=True,
        data=PaymentConfigResponse(
            stripe_enabled=stripe_enabled,
            stripe_publishable_key=publishable_key,
            currency=settings.STRIPE_CURRENCY,
            is_live_mode=is_live_mode,
        ),
    )

@router.post("/create-intent", response_model=ApiResponse[CreatePaymentIntentResponse])
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user = Depends(get_current_user)
):
    """Create Stripe Payment Intent"""
    try:
        # Verify order ownership
        order = await order_service.get_order_by_id(request.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        if str(order.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        result = await payment_service.create_payment_intent(request.order_id)
        
        return ApiResponse(
            success=True,
            data=CreatePaymentIntentResponse(**result)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create payment")

@router.post("/confirm", response_model=ApiResponse[ConfirmPaymentResponse])
async def confirm_payment(
    request: ConfirmPaymentRequest,
    current_user = Depends(get_current_user)
):
    """Confirm payment status"""
    try:
        result = await payment_service.confirm_payment(request.payment_intent_id)
        
        if result["success"]:
            # Send confirmation notification
            order = await order_service.get_order_by_id(result["order_id"])
            if order:
                await notification_service.send_order_confirmation(order)
        
        return ApiResponse(
            success=result["success"],
            data=ConfirmPaymentResponse(**result)
        )
        
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to confirm payment")


# ✅✅✅ BACKGROUND PROCESSING FUNCTION ✅✅✅
async def process_webhook_event(event):
    """
    Process webhook event asynchronously AFTER returning 200 OK to Stripe.
    This ensures Stripe receives acknowledgment quickly.
    """
    try:
        logger.info(f"🔄 Processing webhook event: {event.type}")
        
        # Handle payment_intent.succeeded
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            order_id = payment_intent.metadata.get("order_id")
            
            if order_id:
                logger.info(f"💰 Payment succeeded for order: {order_id}")
                
                # Update order payment status
                try:
                    await order_service.update_payment_status(
                        order_id, 
                        "paid", 
                        payment_intent.id
                    )
                    logger.info(f"✅ Order {order_id} marked as paid")
                except Exception as e:
                    logger.error(f"❌ Failed to update order {order_id}: {e}")
                    # Don't raise - we already acknowledged the webhook
                
                # Send notification (non-blocking)
                try:
                    order = await order_service.get_order_by_id(order_id)
                    if order:
                        await notification_service.send_order_confirmation(order)
                        logger.info(f"📧 Confirmation sent for order {order_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send notification for order {order_id}: {e}")
                    # Don't raise - notification failure shouldn't fail webhook
            else:
                logger.warning("⚠️ payment_intent.succeeded without order_id in metadata")
        
        # Handle payment_intent.payment_failed
        elif event.type == "payment_intent.payment_failed":
            payment_intent = event.data.object
            order_id = payment_intent.metadata.get("order_id")
            
            if order_id:
                logger.warning(f"❌ Payment failed for order: {order_id}")
                
                try:
                    await order_service.update_payment_status(order_id, "failed")
                    logger.info(f"✅ Order {order_id} marked as failed")
                except Exception as e:
                    logger.error(f"❌ Failed to update failed order {order_id}: {e}")
            else:
                logger.warning("⚠️ payment_intent.payment_failed without order_id in metadata")
        
        # Handle charge.succeeded (for compatibility)
        elif event.type == "charge.succeeded":
            charge = event.data.object
            payment_intent_id = charge.payment_intent
            
            if payment_intent_id:
                logger.info(f"💳 Charge succeeded for payment_intent: {payment_intent_id}")
            else:
                logger.warning("⚠️ charge.succeeded without payment_intent")
        
        # Handle charge.failed
        elif event.type == "charge.failed":
            charge = event.data.object
            logger.warning(f"❌ Charge failed: {charge.id}")
        
        else:
            logger.info(f"ℹ️ Unhandled webhook event type: {event.type}")
        
        logger.info(f"✅ Webhook processing complete: {event.type}")
        
    except Exception as e:
        # Log the error but don't raise - webhook was already acknowledged
        logger.error(f"❌ Error processing webhook {event.type}: {e}", exc_info=True)


# ✅✅✅ WEBHOOK ENDPOINT - FIXED VERSION ✅✅✅
@router.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handle Stripe webhooks with explicit JSONResponse.
    
    CRITICAL FIXES:
    1. Use JSONResponse for explicit headers
    2. Set status_code=200 explicitly
    3. Return BEFORE any async operations
    """
    
    try:
        # Step 1: Get raw payload (this is fast)
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        # Step 2: Verify signature (this might be slow, but necessary before responding)
        try:
            event = stripe_client.verify_webhook_signature(payload, sig_header)
            logger.info(f"✅ Webhook received: {event.type} (ID: {event.id})")
        except ValueError as e:
            logger.error(f"❌ Invalid webhook payload: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid payload"},
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logger.error(f"❌ Webhook signature verification failed: {e}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid signature"},
                headers={"Content-Type": "application/json"}
            )
        
        # Step 3: Schedule background processing
        background_tasks.add_task(process_webhook_event, event)
        
        # Step 4: Return 200 OK IMMEDIATELY with explicit headers
        return JSONResponse(
            status_code=200,
            content={
                "status": "received",
                "event_id": event.id,
                "event_type": event.type
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Unexpected webhook error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
            headers={"Content-Type": "application/json"}
        )


@router.post("/refund", response_model=ApiResponse[dict])
async def process_refund(
    request: RefundRequest,
    current_user = Depends(get_current_user)
):
    """Process refund (Admin only or customer request)"""
    try:
        # Verify order ownership or admin
        order = await order_service.get_order_by_id(request.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        if str(order.user_id) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        result = await payment_service.process_refund(request.order_id, request.amount, request.reason)
        
        return ApiResponse(
            success=result["success"],
            data=result,
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process refund")
