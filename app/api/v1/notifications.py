from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.schemas.response import ApiResponse
from app.services.notification_service import notification_service
from app.services.order_service import order_service
from app.middleware.auth_middleware import get_current_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])

class SendNotificationRequest(BaseModel):
    order_id: str

@router.post("/send-confirmation", response_model=ApiResponse[dict])
async def send_order_confirmation(
    request: SendNotificationRequest,
    current_admin = Depends(get_current_admin)
):
    """Send order confirmation notification"""
    try:
        order = await order_service.get_order_by_id(request.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        success = await notification_service.send_order_confirmation(order)
        
        return ApiResponse(
            success=success,
            message="Notification sent" if success else "Failed to send notification"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send notification")
