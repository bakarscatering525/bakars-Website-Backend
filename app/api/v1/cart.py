from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.cart import CartSummary, AddToCartRequest, UpdateCartItemRequest
from app.schemas.response import ApiResponse
from app.services.cart_service import cart_service
from app.middleware.auth_middleware import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/summary", response_model=ApiResponse[CartSummary])
async def get_cart_summary(current_user = Depends(get_current_user)):
    """Get cart summary"""
    try:
        summary = await cart_service.get_cart_summary(str(current_user.id))
        
        return ApiResponse(
            success=True,
            data=CartSummary(**summary)
        )
    except Exception as e:
        logger.error(f"Error fetching cart: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch cart")

@router.post("/add-item", response_model=ApiResponse[CartSummary])
async def add_to_cart(
    request: AddToCartRequest,
    current_user = Depends(get_current_user)
):
    """Add item to cart"""
    try:
        summary = await cart_service.add_to_cart(
            str(current_user.id),
            request.item_id,
            request.quantity,
            request.variation_size,
        )
        
        return ApiResponse(
            success=True,
            data=CartSummary(**summary),
            message="Item added to cart"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add item")

@router.put("/update-item/{item_id}", response_model=ApiResponse[CartSummary])
async def update_cart_item(
    item_id: str,
    request: UpdateCartItemRequest,
    current_user = Depends(get_current_user)
):
    """Update cart item quantity"""
    try:
        summary = await cart_service.update_cart_item(
            str(current_user.id),
            item_id,
            request.quantity,
            request.variation_size,
        )
        
        return ApiResponse(
            success=True,
            data=CartSummary(**summary),
            message="Cart updated"
        )
    except Exception as e:
        logger.error(f"Error updating cart: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update cart")

@router.delete("/remove-item/{item_id}", response_model=ApiResponse[CartSummary])
async def remove_from_cart(
    item_id: str,
    variation_size: str = None,
    current_user = Depends(get_current_user)
):
    """Remove item from cart"""
    try:
        summary = await cart_service.remove_from_cart(
            str(current_user.id),
            item_id,
            variation_size,
        )
        
        return ApiResponse(
            success=True,
            data=CartSummary(**summary),
            message="Item removed from cart"
        )
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove item")

@router.post("/clear", response_model=ApiResponse[dict])
async def clear_cart(current_user = Depends(get_current_user)):
    """Clear entire cart"""
    try:
        success = await cart_service.clear_cart(str(current_user.id))
        
        return ApiResponse(
            success=success,
            message="Cart cleared"
        )
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to clear cart")
