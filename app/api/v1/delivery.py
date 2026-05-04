from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.schemas.response import ApiResponse, DeliveryCheckResponse
from app.services.delivery_service import delivery_service
from app.utils.constants import DAILY_DELIVERY_FEE, DAILY_DELIVERY_RADIUS
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/delivery", tags=["Delivery"])

class CheckAvailabilityRequest(BaseModel):
    address: str
    order_type: str  # daily, weekly, catering

class CalculateFeeRequest(BaseModel):
    address: str
    order_value: float
    delivery_days: int = 1
    is_express: bool = False

@router.post("/check-availability", response_model=ApiResponse[DeliveryCheckResponse])
async def check_delivery_availability(request: CheckAvailabilityRequest):
    """Check if address is within delivery range"""
    try:
        if request.order_type == "daily":
            is_available, distance, geocoded, failure_reason = await delivery_service.check_daily_delivery(request.address)
            
            if is_available:
                return ApiResponse(
                    success=True,
                    data=DeliveryCheckResponse(
                        available=True,
                        distance_km=distance,
                        delivery_fee=DAILY_DELIVERY_FEE,
                        message="Delivery available to this address"
                    )
                )
            else:
                reason = failure_reason or (
                    f"Daily delivery is only available within {DAILY_DELIVERY_RADIUS:.0f}km of Guildford."
                    if distance is None
                    else f"Address is {distance:.1f}km away. Daily delivery is limited to {DAILY_DELIVERY_RADIUS:.0f}km."
                )
                return ApiResponse(
                    success=True,
                    data=DeliveryCheckResponse(
                        available=False,
                        distance_km=distance,
                        message=reason
                    )
                )
        else:
            # Weekly/Catering - must match an active delivery zone (postcode-based)
            postcode = delivery_service._extract_postcode(request.address)
            zone = await delivery_service._find_zone_by_postcode(postcode)
            if not zone:
                return ApiResponse(
                    success=True,
                    data=DeliveryCheckResponse(
                        available=False,
                        message="Delivery is not available to this postcode."
                    )
                )
            return ApiResponse(
                success=True,
                data=DeliveryCheckResponse(
                    available=True,
                    delivery_fee=zone.get("base_delivery_fee"),
                    message="Delivery available. Fee will be calculated at checkout."
                )
            )
            
    except Exception as e:
        logger.error(f"Error checking delivery availability: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check availability")

@router.post("/calculate-fee", response_model=ApiResponse[dict])
async def calculate_delivery_fee(request: CalculateFeeRequest):
    """Calculate delivery fee for weekly orders"""
    try:
        delivery_fee, distance, geocoded = await delivery_service.calculate_weekly_delivery_fee(
            request.address,
            request.order_value,
            request.delivery_days,
            request.is_express
        )
        
        return ApiResponse(
            success=True,
            data={
                "delivery_fee": delivery_fee,
                "distance_km": distance,
                "delivery_days": request.delivery_days,
                "is_express": request.is_express,
                "formatted_address": geocoded["formatted_address"]
            }
        )
    except ValueError as ve:
        logger.warning(f"Delivery fee calculation rejected: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error calculating delivery fee: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate fee")

@router.get("/zones", response_model=ApiResponse[list])
async def get_delivery_zones():
    """Get list of available delivery suburbs"""
    try:
        suburbs = await delivery_service.get_available_suburbs()
        
        return ApiResponse(
            success=True,
            data=suburbs
        )
    except Exception as e:
        logger.error(f"Error fetching delivery zones: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch zones")

@router.post("/check-postcode", response_model=ApiResponse[dict])
async def check_postcode(postcode: str):
    """Check if postcode is covered"""
    try:
        result = await delivery_service.check_postcode_coverage(postcode)
        
        return ApiResponse(
            success=True,
            data=result
        )
    except Exception as e:
        logger.error(f"Error checking postcode: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check postcode")
