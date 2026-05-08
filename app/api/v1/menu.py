from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Query
from typing import List, Optional, Union
from math import ceil
from app.schemas.menu import (
    MenuItemResponse, CategoryResponse,
    WeeklyMenuResponse, CateringPackageResponse,
    CreateMenuItemRequest, UpdateMenuItemRequest,
    PaginationMeta, PaginatedMenuItemsResponse,
    DailyMenuAvailabilityResponse,
)
from app.schemas.response import ApiResponse
from app.schemas.subscription import MealSubscriptionPlanResponse
from app.services.menu_service import menu_service
from app.services.subscription_service import meal_subscription_service
from app.config.r2_client import r2_client
from app.config.settings import settings
from app.middleware.auth_middleware import get_current_admin
from app.utils.time_windows import get_daily_menu_status
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/menu", tags=["Menu"])

def fix_image_url(image_url: str | None) -> str | None:
    """Fix image URLs that use the old R2 storage endpoint"""
    if not image_url:
        return None

    # Already a correct URL
    if image_url.startswith('http://') or image_url.startswith('https://'):
        # Check if it's using the old R2 storage endpoint
        if '.r2.cloudflarestorage.com/' in image_url:
            # Extract the path from the old URL
            try:
                parts = image_url.split('.r2.cloudflarestorage.com/')
                if len(parts) > 1:
                    path = parts[1]
                    # Construct new URL with the public endpoint
                    if settings.R2_PUBLIC_URL:
                        return f"{settings.R2_PUBLIC_URL}/{path}"
            except Exception as e:
                logger.warning(f"Could not fix image URL: {image_url}, error: {e}")
        
        return image_url

    # Data URL
    if image_url.startswith('data:'):
        return image_url

    # Relative URL - construct absolute URL
    if settings.R2_PUBLIC_URL:
        path = image_url.lstrip('/')
        return f"{settings.R2_PUBLIC_URL}/{path}"

    return image_url

def get_absolute_image_url(image_url: str | None) -> str | None:
    """Convert relative image URLs to absolute URLs and fix old URLs"""
    return fix_image_url(image_url)

def item_to_response(item) -> MenuItemResponse:
    """Convert menu item model to response with absolute image URL"""
    image_url = get_absolute_image_url(item.image_url)

    return MenuItemResponse(
        id=str(item.id),
        _id=str(item.id),
        name=item.name,
        description=item.description,
        category=item.category,
        price=item.price,
        variations=getattr(item, 'variations', []) or [],
        image_url=image_url,
        is_available=item.is_available,
        is_available_for_daily=item.is_available_for_daily,
        is_available_for_meal_plan=item.is_available_for_meal_plan,
        allergens=item.allergens or [],
        spice_level=item.spice_level,
        is_vegetarian=item.is_vegetarian,
        is_vegan=getattr(item, 'is_vegan', False),
        is_halal=item.is_halal,
        nutritional_info=getattr(item, 'nutritional_info', None),
        serving_size=getattr(item, 'serving_size', None),
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat()
    )

@router.get(
    "/daily/status",
    response_model=ApiResponse[DailyMenuAvailabilityResponse],
)
async def get_daily_menu_availability():
    """Return the current availability window for Daily Menu orders."""
    status = get_daily_menu_status()
    payload = DailyMenuAvailabilityResponse(
        is_open=status["is_open"],
        window_label=status["window_label"],
        timezone=status["timezone"],
        opens_at=status["opens_at"].isoformat(),
        closes_at=status["closes_at"].isoformat(),
        current_time=status["current_time"].isoformat(),
        message=status["message"],
    )

    return ApiResponse(
        success=True,
        data=payload,
        message=status.get("message"),
    )

@router.get(
    "/daily",
    response_model=ApiResponse[Union[List[MenuItemResponse], PaginatedMenuItemsResponse]],
)
async def get_daily_menu(
    category: Optional[str] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    is_vegetarian: Optional[bool] = None,
    is_vegan: Optional[bool] = None,
    search: Optional[str] = None,
):
    """Get daily menu items"""
    try:
        logger.info(f"GET /menu/daily - category: {category}")
        is_paginated = page is not None and page_size is not None

        filter_params = {
            "category": category,
            "is_vegetarian": is_vegetarian,
            "is_vegan": is_vegan,
            "search": search,
        }

        if is_paginated:
            skip = (page - 1) * page_size
            items, total = await menu_service.get_daily_menu_paginated(
                filter_params, skip, page_size
            )
        else:
            items = await menu_service.get_daily_menu(filter_params)
            total = len(items)

        logger.info(f"Retrieved {len(items)} daily menu items from service")

        # Convert all items and ensure image URLs are absolute
        response_items = [item_to_response(item) for item in items]

        if response_items:
            first_item = response_items[0]
            logger.info(
                "Converted %s items. Sample item: %s (image: %s)"
                % (len(response_items), first_item.name, first_item.image_url)
            )
        else:
            logger.warning("No items in response!")

        if not is_paginated:
            return ApiResponse(
                success=True,
                data=response_items
            )

        total_pages = max(1, -(-total // page_size)) if page_size else 1

        return ApiResponse(
            success=True,
            data=PaginatedMenuItemsResponse(
                items=response_items,
                pagination=PaginationMeta(
                    page=page or 1,
                    page_size=page_size or len(response_items) or 1,
                    total_items=total,
                    total_pages=total_pages,
                ),
            ),
        )
    except Exception as e:
        logger.error(f"Error fetching daily menu: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch menu: {str(e)}"
        )

@router.get("/subscription/plans", response_model=ApiResponse[List[MealSubscriptionPlanResponse]])
async def get_meal_subscription_plans(tab: Optional[str] = None):
    """Public endpoint to fetch active meal subscription plans."""
    try:
        plan_models, _total = await meal_subscription_service.list_plans(tab)
        response_plans: List[MealSubscriptionPlanResponse] = []
        for plan in plan_models:
            plan_data = (
                plan.model_dump(by_alias=True)
                if hasattr(plan, "model_dump")
                else plan.dict(by_alias=True)
            )
            raw_id = getattr(plan, "id", None) or plan_data.get("_id")
            if raw_id is not None:
                plan_data["_id"] = str(raw_id)
            response_plans.append(MealSubscriptionPlanResponse(**plan_data))
        return ApiResponse(
            success=True,
            data=response_plans
        )
    except Exception as e:
        logger.error(f"Error fetching meal subscription plans: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meal subscription plans"
        )

@router.get("/weekly", response_model=ApiResponse[WeeklyMenuResponse])
async def get_weekly_menu(
    delivery_date: str,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
):
    """Get weekly menu for specific delivery date"""
    try:
        logger.info(f"📍 Fetching weekly menu for date: {delivery_date}")
        menu_data = await menu_service.get_weekly_menu(delivery_date)

        if not menu_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found for this date"
            )

        response_items = [item_to_response(item) for item in menu_data["items"]]
        paginated_items = response_items
        pagination_meta = None

        if page is not None and page_size is not None:
            total_items = len(response_items)
            total_pages = max(1, ceil(total_items / page_size)) if page_size else 1
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_items = response_items[start_index:end_index]
            pagination_meta = PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
            )

        return ApiResponse(
            success=True,
            data=WeeklyMenuResponse(
                delivery_date=menu_data["delivery_date"],
                menu_rotation=menu_data["menu_rotation"],
                items=paginated_items,
                pagination=pagination_meta,
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching weekly menu: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch menu"
        )

@router.get("/catering", response_model=ApiResponse[List[MenuItemResponse]])
async def get_catering_menu(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200)
):
    """Catering menu is now managed offline; respond with empty list and info message."""
    logger.info("Catering menu requested via API; returning informational stub response.")
    return ApiResponse(
        success=True,
        data=[],
        message="Catering enquiries are handled directly. Please contact the team for bespoke menus."
    )

@router.get("/categories", response_model=ApiResponse[List[CategoryResponse]])
async def get_categories(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200)
):
    """Get all food categories"""
    try:
        logger.info("📍 Fetching categories")
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            categories, _ = await menu_service.get_all_categories_paginated(False, skip, page_size)
        else:
            categories = await menu_service.get_categories()

        response_cats = [
            CategoryResponse(
                id=str(cat.id),
                _id=str(cat.id),
                name=cat.name,
                display_name=cat.display_name,
                description=cat.description,
                image_url=get_absolute_image_url(cat.image_url),
                is_active=cat.is_active,
                sort_order=cat.sort_order
            )
            for cat in categories
        ]

        logger.info(f"✅ Retrieved {len(response_cats)} categories")

        return ApiResponse(
            success=True,
            data=response_cats
        )
    except Exception as e:
        logger.error(f"❌ Error fetching categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )

@router.get("/items/{item_id}", response_model=ApiResponse[MenuItemResponse])
async def get_menu_item(item_id: str):
    """Get specific menu item"""
    try:
        logger.info(f"📍 Fetching menu item: {item_id}")
        item = await menu_service.get_menu_item_by_id(item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )

        return ApiResponse(
            success=True,
            data=item_to_response(item)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch menu item"
        )

# ✅ Admin endpoints
@router.post("/items", response_model=ApiResponse[MenuItemResponse])
async def create_menu_item(
    request: CreateMenuItemRequest,
    _: str = Depends(get_current_admin)
):
    """Create new menu item (Admin only)"""
    try:
        created_item = await menu_service.create_menu_item(request.dict())
        return ApiResponse(
            success=True,
            data=item_to_response(created_item),
            message="Menu item created successfully"
        )
    except Exception as e:
        logger.error(f"❌ Error creating menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create menu item"
        )

@router.put("/items/{item_id}", response_model=ApiResponse[MenuItemResponse])
async def update_menu_item(
    item_id: str,
    request: UpdateMenuItemRequest,
    _: str = Depends(get_current_admin)
):
    """Update menu item (Admin only)"""
    try:
        item = await menu_service.update_menu_item(item_id, request.dict(exclude_unset=True))
        return ApiResponse(
            success=True,
            data=item_to_response(item),
            message="Menu item updated successfully"
        )
    except Exception as e:
        logger.error(f"❌ Error updating menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update menu item"
        )

@router.delete("/items/{item_id}")
async def delete_menu_item(
    item_id: str,
    _: str = Depends(get_current_admin)
):
    """Delete menu item (Admin only)"""
    try:
        await menu_service.delete_menu_item(item_id)
        return ApiResponse(
            success=True,
            message="Menu item deleted successfully"
        )
    except Exception as e:
        logger.error(f"❌ Error deleting menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete menu item"
        )
