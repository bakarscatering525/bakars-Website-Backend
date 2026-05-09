from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, Any
from app.schemas.order import (
    CreateDailyOrderRequest, CreateMealSubscriptionOrderRequest, CreateCateringOrderRequest,
    OrderResponse, OrderListResponse, UpdateOrderStatusRequest, UpdateMealSubscriptionOrderRequest,
    UpdateDeliverySlotMenuItemsRequest,
)
from app.schemas.auth import AddressSchema
from app.schemas.response import ApiResponse
from app.services.order_service import order_service
from app.services.auth_service import auth_service
from app.services.notification_service import notification_service
from app.middleware.auth_middleware import get_current_user
from app.config.settings import settings
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])

def order_to_response(order) -> OrderResponse:
    """Convert order model to response schema"""
    # Normalize delivery address data before feeding into the response schema.
    delivery_address = None
    raw_address: Any = getattr(order, "delivery_address", None)
    if raw_address:
        if isinstance(raw_address, AddressSchema):
            delivery_address = raw_address
        elif isinstance(raw_address, dict):
            try:
                delivery_address = AddressSchema(**raw_address)
            except ValidationError:
                delivery_address = None

    # The order already has OrderItem objects with all fields as primitives
    return OrderResponse(
        id=str(order.id),
        order_number=order.order_number,
        order_type=order.order_type,
        status=order.status,
        payment_status=order.payment_status,
        items=order.items,
        sidelines=getattr(order, "sidelines", []),
        subtotal=order.subtotal,
        discount_amount=getattr(order, "discount_amount", 0.0),
        tax_amount=getattr(order, "tax_amount", 0.0),
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        delivery_method=order.delivery_method,
        delivery_address_id=getattr(order, "delivery_address_id", None),
        delivery_address=delivery_address,
        created_at=order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at),
        payment_intent_id=order.stripe_payment_intent_id,
        payment_method=order.payment_method,
        primary_plan_tab=getattr(order, "primary_plan_tab", None),
        primary_plan_name=getattr(order, "primary_plan_name", None),
        extra_boxes=getattr(order, "extra_boxes", 0),
        extra_boxes_price=getattr(order, "extra_boxes_price", 0.0),
        plan_price_total=getattr(order, "plan_price_total", 0.0),
    )

@router.post("/daily", response_model=ApiResponse[OrderResponse])
async def create_daily_order(
    request: CreateDailyOrderRequest,
    current_user = Depends(get_current_user)
):
    """Create daily menu order"""
    try:
        # Get delivery address
        if request.delivery_method == "standard":
            if not request.delivery_address_id:
                raise ValueError("Delivery address required")
            
            user = await auth_service.get_user_by_id(str(current_user.id))
            delivery_address = None
            for addr in user.addresses:
                if str(addr.get("_id")) == request.delivery_address_id:
                    delivery_address = addr
                    break
            
            if not delivery_address:
                raise ValueError("Delivery address not found")
        else:
            delivery_address = None
        
        # Create order
        order = await order_service.create_daily_order(
            str(current_user.id),
            request.items,
            request.delivery_method,
            delivery_address.dict() if delivery_address else {},
            request.delivery_instructions,
            request.notes,
            request.payment_method,
        )
        
        payment_method = (request.payment_method or "cash").lower()
        if payment_method != "card":
            try:
                await notification_service.send_order_confirmation(order)
            except Exception as notify_error:
                logger.error("Failed to send daily order confirmation: %s", notify_error)
        
        # Clear cart after successful order
        try:
            from app.services.cart_service import cart_service
            await cart_service.clear_cart(str(current_user.id))
        except Exception as e:
            logger.warning(f"Failed to clear cart after order: {e}")
        
        return ApiResponse(
            success=True,
            data=order_to_response(order),
            message="Order created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating daily order: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")

@router.post("/weekly", response_model=ApiResponse[OrderResponse])
async def create_meal_subscription_order(
    request: CreateMealSubscriptionOrderRequest,
    current_user = Depends(get_current_user)
):
    """Create meal subscription order"""
    try:
        delivery_payload = {}
        if request.fulfilment_method == "delivery":
            if not request.delivery_address_id:
                raise ValueError("Delivery address required for delivery orders")

            user = await auth_service.get_user_by_id(str(current_user.id))
            delivery_address = None
            for addr in user.addresses:
                if str(addr.get("_id")) == request.delivery_address_id:
                    delivery_address = addr
                    break

            if not delivery_address:
                raise ValueError("Delivery address not found")

            delivery_payload = delivery_address.dict()

        order, _subscription = await order_service.create_meal_subscription_order(
            str(current_user.id),
            [selection.dict() for selection in request.plan_selections],
            [slot.dict() for slot in request.delivery_slots],
            request.sidelines,
            delivery_payload,
            request.fulfilment_method,
            request.is_express,
            request.delivery_instructions,
            request.notes,
            request.payment_method,
            request.delivery_address_id,
        )

        payment_method = (request.payment_method or "cash").lower()
        if payment_method != "card":
            try:
                await notification_service.send_order_confirmation(order)
            except Exception as notify_error:
                logger.error("Failed to send subscription order confirmation: %s", notify_error)
        
        return ApiResponse(
            success=True,
            data=order_to_response(order),
            message="Meal subscription created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating meal subscription order: {e}", exc_info=True)
        detail = str(e) if settings.ENVIRONMENT != "production" else "Failed to create order"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

@router.get("/weekly/{order_id}", response_model=ApiResponse[dict])
async def get_meal_subscription_details(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """Fetch meal subscription order details for editing"""
    try:
        details = await order_service.get_meal_subscription_details(
            order_id,
            str(current_user.id),
        )
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal subscription not found",
            )
        return ApiResponse(success=True, data=details)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error loading meal subscription details: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load subscription details",
        )

@router.put("/weekly/{order_id}", response_model=ApiResponse[OrderResponse])
async def update_meal_subscription_order(
    order_id: str,
    request: UpdateMealSubscriptionOrderRequest,
    current_user = Depends(get_current_user)
):
    """Update an existing meal subscription order"""
    try:
        delivery_payload = {}
        if request.fulfilment_method == "delivery":
            if not request.delivery_address_id:
                raise ValueError("Delivery address required for delivery orders")

            user = await auth_service.get_user_by_id(str(current_user.id))
            delivery_address = None
            for addr in user.addresses:
                if str(addr.get("_id")) == request.delivery_address_id:
                    delivery_address = addr
                    break

            if not delivery_address:
                raise ValueError("Delivery address not found")

            delivery_payload = delivery_address.dict()

        order = await order_service.update_meal_subscription_order(
            order_id,
            str(current_user.id),
            [selection.dict() for selection in request.plan_selections],
            [slot.dict() for slot in request.delivery_slots],
            request.sidelines,
            delivery_payload,
            request.fulfilment_method,
            request.is_express,
            request.delivery_instructions,
            request.notes,
            request.payment_method,
            request.delivery_address_id,
        )

        return ApiResponse(
            success=True,
            data=order_to_response(order),
            message="Meal subscription updated successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating meal subscription order: %s", e, exc_info=True)
        detail = str(e) if settings.ENVIRONMENT != "production" else "Failed to update order"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

@router.patch("/weekly/{order_id}/delivery-slot", response_model=ApiResponse[OrderResponse])
async def update_subscription_delivery_slot(
    order_id: str,
    request: UpdateDeliverySlotMenuItemsRequest,
    current_user = Depends(get_current_user)
):
    """Update menu items for a specific delivery date (customer-facing; respects cutoff)."""
    try:
        updated_order = await order_service.update_delivery_slot_menu_items(
            order_id,
            str(current_user.id),
            request.delivery_date,
            request.menu_items,
            request.notes,
            override_cutoff=False,
            actor_role="user",
        )
        return ApiResponse(
            success=True,
            data=order_to_response(updated_order),
            message="Delivery slot updated",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating delivery slot: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update delivery slot",
        )

@router.post("/catering", response_model=ApiResponse[OrderResponse])
async def create_catering_order(
    request: CreateCateringOrderRequest,
    current_user = Depends(get_current_user)
):
    """Create catering order"""
    try:
        order, catering = await order_service.create_catering_order(
            str(current_user.id),
            request.package_type,
            request.guest_count,
            request.event_date,
            request.event_time,
            request.venue_address,
            request.selected_items,
            request.special_requests,
            request.payment_method,
        )
        
        payment_method = (request.payment_method or "cash").lower()
        if payment_method != "card":
            try:
                await notification_service.send_order_confirmation(order)
            except Exception as notify_error:
                logger.error("Failed to send catering order confirmation email: %s", notify_error)

        # Send catering quote via WhatsApp
        await notification_service.send_catering_quote(order, catering)
        
        return ApiResponse(
            success=True,
            data=order_to_response(order),
            message="Catering order created. Quote sent via WhatsApp."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating catering order: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")

@router.get("/my-orders", response_model=ApiResponse[OrderListResponse])
async def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get user's orders"""
    try:
        skip = (page - 1) * page_size
        orders, total = await order_service.get_user_orders(str(current_user.id), skip, page_size)

        return ApiResponse(
            success=True,
            data=OrderListResponse(
                orders=[order_to_response(order) for order in orders],
                total=total,
                page=page,
                page_size=page_size
            )
        )
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch orders")

@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """Get specific order"""
    try:
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        # Verify ownership
        if str(order.user_id) != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return ApiResponse(
            success=True,
            data=order_to_response(order)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch order")
