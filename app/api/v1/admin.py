from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import json
import logging

from app.schemas.response import ApiResponse
from app.schemas.menu import MenuItemResponse, CategoryResponse, PaginatedMenuItemsResponse, PaginationMeta
from app.schemas.subscription import MealSubscriptionPlanResponse, DeliveryZoneResponse
from app.services.menu_service import menu_service
from app.services.admin_service import admin_service
from app.services.subscription_service import meal_subscription_service
from app.services.delivery_service import delivery_service
from app.services.reminder_service import reminder_service
from app.services.order_service import order_service
from app.config.r2_client import r2_client
from app.middleware.auth_middleware import get_current_admin
from app.schemas.order import UpdateOrderStatusRequest, UpdateDeliverySlotMenuItemsRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

AVAILABILITY_SCOPE_ALIASES = {
    "daily": "daily",
    "daily_only": "daily",
    "daily_menu": "daily",
    "daily_menu_only": "daily",
    "meal_plan": "meal_plan",
    "mealplan": "meal_plan",
    "meal_plan_only": "meal_plan",
    "weekly": "meal_plan",
    "weekly_menu": "meal_plan",
    "both": "both",
    "all": "both",
    "daily_and_meal_plan": "both",
}

SCOPE_TO_FLAGS: Dict[str, Tuple[bool, bool]] = {
    "daily": (True, False),
    "meal_plan": (False, True),
    "both": (True, True),
}


def normalize_availability_scope(scope_value: Optional[str]) -> Optional[str]:
    """Normalize incoming scope strings to the supported set."""
    if scope_value is None:
        return None

    normalized = scope_value.strip().lower()
    if not normalized:
        return None
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = "_".join(filter(None, normalized.split("_")))

    resolved = AVAILABILITY_SCOPE_ALIASES.get(normalized, normalized)
    if resolved in SCOPE_TO_FLAGS:
        return resolved

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid availability_scope. Use 'daily', 'meal_plan', or 'both'.",
    )


def determine_scope_from_flags(is_daily: bool, is_meal_plan: bool) -> str:
    """Convert boolean flags back to the canonical scope label."""
    if is_daily and is_meal_plan:
        return "both"
    if is_daily:
        return "daily"
    return "meal_plan"


def resolve_availability_flags(
    scope_override: Optional[str],
    scope_field: Optional[str],
    explicit_daily: Optional[bool],
    explicit_meal_plan: Optional[bool],
) -> Tuple[str, bool, bool]:
    """Resolve final availability booleans using overrides, scope field, or explicit flags."""
    for candidate in (scope_override, scope_field):
        if candidate is None:
            continue
        normalized = normalize_availability_scope(candidate)
        if normalized:
            flags = SCOPE_TO_FLAGS[normalized]
            return normalized, flags[0], flags[1]

    daily_flag = explicit_daily if explicit_daily is not None else True
    meal_plan_flag = explicit_meal_plan if explicit_meal_plan is not None else False

    if not daily_flag and not meal_plan_flag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Select at least one availability option (daily, meal plan, or both).",
        )

    normalized_scope = determine_scope_from_flags(daily_flag, meal_plan_flag)
    return normalized_scope, daily_flag, meal_plan_flag


def parse_allergens_field(raw_allergens: Optional[str]) -> List[str]:
    """Accept comma separated or JSON list allergens and normalize to a list."""
    if not raw_allergens:
        return []

    value = raw_allergens.strip()
    if not value:
        return []

    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [
                str(allergen).strip()
                for allergen in parsed
                if str(allergen).strip()
            ]
    except json.JSONDecodeError:
        pass

    return [segment.strip() for segment in value.split(",") if segment.strip()]


async def _upload_menu_item_image(image: Optional[UploadFile]) -> Optional[str]:
    """Upload an image to R2 storage if provided."""
    if not image:
        return None
    content = await image.read()
    return await r2_client.upload_file(
        content,
        image.filename,
        "menu-items",
        image.content_type,
    )


def menu_item_form_params(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    is_available_for_daily: bool = Form(True),
    is_available_for_meal_plan: bool = Form(False),
    allergens: Optional[str] = Form(None),
    spice_level: Optional[str] = Form(None),
    is_vegetarian: bool = Form(False),
    is_halal: bool = Form(True),
    availability_scope: Optional[str] = Form(
        None, description="daily | meal_plan | both (optional override)"
    ),
) -> Dict[str, Any]:
    """Collect common menu item creation form parameters."""
    return {
        "name": name,
        "category": category,
        "price": price,
        "description": description,
        "is_available_for_daily": is_available_for_daily,
        "is_available_for_meal_plan": is_available_for_meal_plan,
        "allergens": allergens,
        "spice_level": spice_level,
        "is_vegetarian": is_vegetarian,
        "is_halal": is_halal,
        "availability_scope": availability_scope,
    }


async def _create_menu_item_from_form(
    form_data: Dict[str, Any],
    image: Optional[UploadFile],
    scope_override: Optional[str] = None,
) -> ApiResponse[dict]:
    """Shared logic for creating menu items with consistent availability handling."""
    try:
        image_url = await _upload_menu_item_image(image)
        allergens_list = parse_allergens_field(form_data.get("allergens"))
        scope_label, is_daily, is_meal_plan = resolve_availability_flags(
            scope_override,
            form_data.get("availability_scope"),
            form_data.get("is_available_for_daily"),
            form_data.get("is_available_for_meal_plan"),
        )

        item_payload = {
            "name": form_data["name"],
            "category": form_data["category"],
            "price": form_data["price"],
            "description": form_data.get("description"),
            "is_available_for_daily": is_daily,
            "is_available_for_meal_plan": is_meal_plan,
            "allergens": allergens_list,
            "spice_level": form_data.get("spice_level"),
            "is_vegetarian": form_data.get("is_vegetarian", False),
            "is_halal": form_data.get("is_halal", True),
        }

        created_item = await menu_service.create_menu_item(item_payload, image_url)
        scope_messages = {
            "daily": "Daily Menu",
            "meal_plan": "Meal Plan Menu",
            "both": "Daily & Meal Plan menus",
        }

        return ApiResponse(
            success=True,
            data={
                "item": MenuItemResponse.from_model(created_item),
                "id": str(created_item.id),
                "availability_scope": scope_label,
            },
            message=f"Menu item created for {scope_messages.get(scope_label, 'selected menus')}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu item: {str(e)}",
        )

# ============= DASHBOARD =============

@router.get("/dashboard", response_model=ApiResponse[dict])
async def get_dashboard_stats(
    current_admin = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    try:
        stats = await admin_service.get_dashboard_stats()
        return ApiResponse(
            success=True,
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

# ============= ORDERS WITH PAGINATION =============

@router.get("/orders", response_model=ApiResponse[dict])
async def get_all_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(8, ge=1, le=200, description="Items per page"),  # ✅ UPDATED: Changed default from 20 to 8
    status: Optional[str] = Query(None, description="Filter by order status"),
    order_type: Optional[str] = Query(None, description="Filter by order type"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by order number or ID"),
    current_admin = Depends(get_current_admin)
):
    """Get all orders with pagination and filters"""
    try:
        skip = (page - 1) * page_size
        
        # Parse dates if provided
        date_from_obj = None
        date_to_obj = None
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD"
                )
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
                # Set to end of day
                date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD"
                )
        
        orders, total = await admin_service.get_all_orders(
            skip=skip,
            limit=page_size,
            status=status,
            order_type=order_type,
            date_from=date_from_obj,
            date_to=date_to_obj,
            search=search,
        )
        
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        
        return ApiResponse(
            success=True,
            data={
                "orders": orders,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get orders: {str(e)}"
        )

# ============= ORDER / MENU REPORTS =============

@router.get("/menu-orders", response_model=ApiResponse[dict])
async def get_menu_item_order_report(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page (max 1000 for exports)"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    order_type: Optional[str] = Query(None, description="Filter by order type (daily_menu, meal_subscription)"),
    menu_item_id: Optional[str] = Query(None, description="Filter by menu item id"),
    current_admin = Depends(get_current_admin),
):
    """
    Return aggregated counts of menu items per date across daily orders and meal subscriptions.
    """
    try:
        skip = (page - 1) * page_size

        date_from_obj = None
        date_to_obj = None
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD",
                )
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to)
                date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD",
                )

        results, total = await admin_service.get_menu_item_orders_report(
            skip=skip,
            limit=page_size,
            date_from=date_from_obj,
            date_to=date_to_obj,
            order_type=order_type,
            menu_item_id=menu_item_id,
        )

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

        return ApiResponse(
            success=True,
            data={
                "results": results,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating menu item report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate menu item report",
        )

# ============= ORDER STATUS UPDATE =============

@router.patch("/orders/{order_id}/status", response_model=ApiResponse[dict])
async def update_order_status(
    order_id: str,
    payload: UpdateOrderStatusRequest,
    current_admin = Depends(get_current_admin)
):
    """Update order status"""
    try:
        from app.services.order_service import order_service
        
        updated_order = await order_service.update_order_status(
            order_id,
            payload.status,
            payload.admin_notes
        )
        
        return ApiResponse(
            success=True,
            data={"order": updated_order},
            message=f"Order status updated to {payload.status}"
        )
    except Exception as e:
        logger.error(f"Error updating order status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}"
        )

# ============= MENU ITEMS =============

@router.get("/menu-items", response_model=ApiResponse[dict])
async def get_admin_menu_items(
    include_unavailable: bool = Query(False),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_admin = Depends(get_current_admin)
):
    """Get all menu items for admin with pagination"""
    try:
        logger.info(
            "Fetching menu items: include_unavailable=%s, category=%s, search=%s, page=%s",
            include_unavailable,
            category,
            search,
            page,
        )
        
        skip = (page - 1) * page_size
        items, total = await menu_service.get_all_menu_items_paginated(
            include_unavailable=include_unavailable,
            category=category,
            skip=skip,
            limit=page_size,
            search=search,
        )
        
        logger.info(f"Retrieved {len(items)} items, total={total}")
        
        # Convert models to responses
        response_items = [MenuItemResponse.from_model(item) for item in items]

        stats = await menu_service.get_menu_items_stats()
        
        return ApiResponse(
            success=True,
            data={
                "items": response_items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "stats": stats,
            }
        )
    except Exception as e:
        logger.error(f"Error getting menu items: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get menu items: {str(e)}"
        )

@router.post("/menu-items", response_model=ApiResponse[dict])
async def create_menu_item(
    form_data: Dict[str, Any] = Depends(menu_item_form_params),
    image: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin),
):
    """Create menu item with explicit availability selection."""
    return await _create_menu_item_from_form(form_data, image)


@router.post("/menu-items/daily", response_model=ApiResponse[dict])
async def create_daily_menu_item(
    form_data: Dict[str, Any] = Depends(menu_item_form_params),
    image: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin),
):
    """Create a menu item locked to the daily program."""
    return await _create_menu_item_from_form(form_data, image, scope_override="daily")


@router.post("/menu-items/meal-plan", response_model=ApiResponse[dict])
async def create_meal_plan_menu_item(
    form_data: Dict[str, Any] = Depends(menu_item_form_params),
    image: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin),
):
    """Create a menu item locked to the meal plan program."""
    return await _create_menu_item_from_form(
        form_data, image, scope_override="meal_plan"
    )

@router.put("/menu-items/{item_id}", response_model=ApiResponse[MenuItemResponse])
async def update_menu_item(
    item_id: str,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    is_available_for_daily: Optional[bool] = Form(None),
    is_available_for_meal_plan: Optional[bool] = Form(None),
    availability_scope: Optional[str] = Form(
        None, description="daily | meal_plan | both (optional override)"
    ),
    allergens: Optional[str] = Form(None),
    spice_level: Optional[str] = Form(None),
    is_vegetarian: Optional[bool] = Form(None),
    is_halal: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    remove_image: bool = Form(False),
    current_admin = Depends(get_current_admin)
):
    """Update menu item"""
    try:
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if category is not None:
            update_data["category"] = category
        if price is not None:
            update_data["price"] = price
        if description is not None:
            update_data["description"] = description
        if is_available is not None:
            update_data["is_available"] = is_available
        if is_available_for_daily is not None:
            update_data["is_available_for_daily"] = is_available_for_daily
        if is_available_for_meal_plan is not None:
            update_data["is_available_for_meal_plan"] = is_available_for_meal_plan
        if availability_scope:
            normalized_scope = normalize_availability_scope(availability_scope)
            scope_flags = SCOPE_TO_FLAGS[normalized_scope]
            update_data["is_available_for_daily"] = scope_flags[0]
            update_data["is_available_for_meal_plan"] = scope_flags[1]
        if spice_level is not None:
            update_data["spice_level"] = spice_level
        if is_vegetarian is not None:
            update_data["is_vegetarian"] = is_vegetarian
        if is_halal is not None:
            update_data["is_halal"] = is_halal
        if allergens is not None:
            update_data["allergens"] = parse_allergens_field(allergens)
        
        # Handle image
        if remove_image:
            update_data["image_url"] = None
        elif image:
            content = await image.read()
            image_url = await r2_client.upload_file(
                content,
                image.filename,
                "menu-items",
                image.content_type
            )
            update_data["image_url"] = image_url
        
        updated_item = await menu_service.update_menu_item(item_id, update_data)

        if updated_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found or no changes applied"
            )
        
        return ApiResponse(
            success=True,
            data=MenuItemResponse.from_model(updated_item),
            message="Menu item updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu item: {str(e)}"
        )

@router.delete("/menu-items/{item_id}", response_model=ApiResponse[None])
async def delete_menu_item(
    item_id: str,
    current_admin = Depends(get_current_admin)
):
    """Delete menu item"""
    try:
        await menu_service.delete_menu_item(item_id)
        
        return ApiResponse(
            success=True,
            message="Menu item deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error deleting menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu item: {str(e)}"
        )

# ============= CATEGORIES =============

@router.get("/categories", response_model=ApiResponse[dict])
async def get_admin_categories(
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    current_admin = Depends(get_current_admin)
):
    """Get all categories for admin with pagination"""
    try:
        logger.info(f"Fetching categories: include_inactive={include_inactive}, page={page}")
        
        skip = (page - 1) * page_size
        categories, total = await menu_service.get_all_categories_paginated(
            include_inactive=include_inactive,
            skip=skip,
            limit=page_size
        )
        
        logger.info(f"Retrieved {len(categories)} categories, total={total}")
        
        # Convert models to responses
        response_categories = [CategoryResponse.from_model(cat) for cat in categories]
        
        return ApiResponse(
            success=True,
            data={
                "categories": response_categories,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        logger.error(f"Error getting categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get categories: {str(e)}"
        )

@router.post("/categories", response_model=ApiResponse[CategoryResponse])
async def create_category(
    name: str = Form(...),
    display_name: str = Form(...),
    description: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin)
):
    """Create category"""
    try:
        # Upload image if provided
        image_url = None
        if image:
            content = await image.read()
            image_url = await r2_client.upload_file(
                content,
                image.filename,
                "categories",
                image.content_type
            )
        
        category_data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "sort_order": sort_order,
            "image_url": image_url
        }
        
        created_category = await menu_service.create_category(category_data)
        
        return ApiResponse(
            success=True,
            data=CategoryResponse.from_model(created_category),
            message="Category created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating category: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )

@router.put("/categories/{category_id}", response_model=ApiResponse[CategoryResponse])
async def update_category(
    category_id: str,
    name: Optional[str] = Form(None),
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    remove_image: bool = Form(False),
    current_admin = Depends(get_current_admin)
):
    """Update category"""
    try:
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if display_name is not None:
            update_data["display_name"] = display_name
        if description is not None:
            update_data["description"] = description
        if sort_order is not None:
            update_data["sort_order"] = sort_order
        if is_active is not None:
            update_data["is_active"] = is_active
        
        # Handle image
        if remove_image:
            update_data["image_url"] = None
        elif image:
            content = await image.read()
            image_url = await r2_client.upload_file(
                content,
                image.filename,
                "categories",
                image.content_type
            )
            update_data["image_url"] = image_url
        
        updated_category = await menu_service.update_category(category_id, update_data)
        
        return ApiResponse(
            success=True,
            data=CategoryResponse.from_model(updated_category),
            message="Category updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating category: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}"
        )

@router.delete("/categories/{category_id}", response_model=ApiResponse[None])
async def delete_category(
    category_id: str,
    current_admin = Depends(get_current_admin)
):
    """Delete category"""
    try:
        await menu_service.delete_category(category_id)
        
        return ApiResponse(
            success=True,
            message="Category deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error deleting category: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}"
        )

# ============= MEAL SUBSCRIPTION PLANS =============

@router.get("/meal-plans", response_model=ApiResponse[dict])
async def get_meal_plans(
    tab: Optional[str] = Query(None),
    include_inactive: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_admin = Depends(get_current_admin)
):
    """Get all meal subscription plans for admin"""
    try:
        logger.info(f"Fetching meal plans: tab={tab}, include_inactive={include_inactive}, page={page}")
        
        plans, total = await meal_subscription_service.list_plans(
            tab=tab,
            include_inactive=include_inactive,
            page=page,
            page_size=page_size,
        )
        
        logger.info(f"Retrieved {len(plans)} plans, total={total}")
        
        # Convert plans to dict and manually serialize ObjectIds
        response_plans = []
        for plan in plans:
            plan_dict = plan.dict(by_alias=True) if hasattr(plan, "dict") else {}
            
            # Manually convert all ObjectId fields to strings
            for key, value in plan_dict.items():
                if hasattr(value, '__class__') and value.__class__.__name__ == 'ObjectId':
                    plan_dict[key] = str(value)
            
            # Ensure _id is a string
            if "_id" in plan_dict:
                plan_dict["_id"] = str(plan_dict["_id"])
            
            # Ensure id is a string if present
            if "id" in plan_dict and plan_dict["id"]:
                plan_dict["id"] = str(plan_dict["id"])
            
            response_plans.append(plan_dict)
        
        return ApiResponse(
            success=True,
            data={
                "plans": response_plans,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1
            }
        )
    except Exception as e:
        logger.error(f"Error getting meal plans: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get meal plans: {str(e)}"
        )

@router.post("/meal-plans", response_model=ApiResponse[dict])
async def create_meal_plan(
    payload: dict,
    current_admin = Depends(get_current_admin)
):
    """Create meal subscription plan"""
    try:
        created_plan = await meal_subscription_service.create_plan(payload)
        
        plan_dict = created_plan.dict(by_alias=True)
        if "_id" in plan_dict:
            plan_dict["_id"] = str(plan_dict["_id"])
        
        return ApiResponse(
            success=True,
            data=plan_dict,
            message="Meal plan created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create meal plan: {str(e)}"
        )

@router.put("/meal-plans/{plan_id}", response_model=ApiResponse[dict])
async def update_meal_plan(
    plan_id: str,
    payload: dict,
    current_admin = Depends(get_current_admin)
):
    """Update meal subscription plan"""
    try:
        updated_plan = await meal_subscription_service.update_plan(plan_id, payload)
        
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        plan_dict = updated_plan.dict(by_alias=True)
        if "_id" in plan_dict:
            plan_dict["_id"] = str(plan_dict["_id"])
        
        return ApiResponse(
            success=True,
            data=plan_dict,
            message="Meal plan updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update meal plan: {str(e)}"
        )

@router.delete("/meal-plans/{plan_id}", response_model=ApiResponse[None])
async def delete_meal_plan(
    plan_id: str,
    current_admin = Depends(get_current_admin)
):
    """Delete meal subscription plan"""
    try:
        success = await meal_subscription_service.delete_plan(plan_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        return ApiResponse(
            success=True,
            message="Meal plan deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete meal plan: {str(e)}"
        )

@router.post("/meal-plans/run-reminders", response_model=ApiResponse[dict])
async def run_meal_plan_reminders(
    current_admin = Depends(get_current_admin)
):
    """Trigger reminder dispatch for subscriptions with pending selections."""
    try:
        processed = await reminder_service.process_due_reminders()
        return ApiResponse(
            success=True,
            data={"processed": processed},
            message=f"Processed {processed} reminder(s)"
        )
    except Exception as e:
        logger.error(f"Error processing reminders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run reminders: {str(e)}"
        )

# ============= DELIVERY ZONES =============

@router.get("/delivery-zones", response_model=ApiResponse[dict])
async def get_delivery_zones(
    include_inactive: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, description="Filter by postcode"),
    current_admin = Depends(get_current_admin)
):
    """Get all delivery zones for admin"""
    try:
        logger.info(f"Fetching delivery zones: include_inactive={include_inactive}, page={page}")
        
        # Ensure default zones are seeded
        await delivery_service.ensure_default_zones()
        
        skip = (page - 1) * page_size
        
        if delivery_service.zones is None:
            logger.warning("Delivery zones collection not available")
            return ApiResponse(
                success=True,
                data={
                    "zones": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0
                }
            )
        
        # Build query
        query = {} if include_inactive else {"is_active": True}
        if search and search.strip():
            query["postcode"] = {"$regex": search.strip(), "$options": "i"}
        
        # Get total count
        total = await delivery_service.zones.count_documents(query)
        
        # Get zones with pagination
        cursor = delivery_service.zones.find(query).sort("postcode", 1).skip(skip).limit(page_size)
        zones = await cursor.to_list(length=page_size)
        
        logger.info(f"Retrieved {len(zones)} zones, total={total}")
        
        # Convert to response format
        response_zones = []
        for zone in zones:
            zone["_id"] = str(zone["_id"])
            # Ensure all required fields exist
            zone.setdefault("zone_label", None)
            zone.setdefault("suburbs", [])
            zone.setdefault("state", "NSW")
            zone.setdefault("distance_from_business", None)
            zone.setdefault("base_delivery_fee", 10.0)
            zone.setdefault("express_delivery_fee", None)
            zone.setdefault("max_delivery_days", None)
            zone.setdefault("notes", None)
            zone.setdefault("is_active", True)
            zone.setdefault("order_types", [])
            zone.setdefault("created_at", datetime.utcnow())
            zone.setdefault("updated_at", datetime.utcnow())
            
            response_zones.append(DeliveryZoneResponse(**zone))
        
        return ApiResponse(
            success=True,
            data={
                "zones": response_zones,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1
            }
        )
    except Exception as e:
        logger.error(f"Error getting delivery zones: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get delivery zones: {str(e)}"
        )

@router.post("/delivery-zones", response_model=ApiResponse[DeliveryZoneResponse])
async def create_delivery_zone(
    payload: dict,
    current_admin = Depends(get_current_admin)
):
    """Create delivery zone"""
    try:
        if delivery_service.zones is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delivery zones collection not available"
            )
        
        existing = await delivery_service.zones.find_one({"postcode": payload.get("postcode")})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A delivery zone already exists for this postcode."
            )
        
        zone_data = {
            **payload,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await delivery_service.zones.insert_one(zone_data)
        zone_data["_id"] = str(result.inserted_id)
        
        return ApiResponse(
            success=True,
            data=DeliveryZoneResponse(**zone_data),
            message="Delivery zone created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating delivery zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create delivery zone: {str(e)}"
        )

@router.put("/delivery-zones/{zone_id}", response_model=ApiResponse[DeliveryZoneResponse])
async def update_delivery_zone(
    zone_id: str,
    payload: dict,
    current_admin = Depends(get_current_admin)
):
    """Update delivery zone"""
    try:
        from bson import ObjectId
        
        if delivery_service.zones is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delivery zones collection not available"
            )
        
        if not ObjectId.is_valid(zone_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid zone ID"
            )
        
        update_data = {
            **payload,
            "updated_at": datetime.utcnow()
        }
        
        result = await delivery_service.zones.update_one(
            {"_id": ObjectId(zone_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery zone not found"
            )
        
        # Fetch updated zone
        updated_zone = await delivery_service.zones.find_one({"_id": ObjectId(zone_id)})
        updated_zone["_id"] = str(updated_zone["_id"])
        
        return ApiResponse(
            success=True,
            data=DeliveryZoneResponse(**updated_zone),
            message="Delivery zone updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating delivery zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update delivery zone: {str(e)}"
        )

@router.patch("/orders/{order_id}/delivery-slot", response_model=ApiResponse[dict])
async def admin_update_delivery_slot(
    order_id: str,
    payload: UpdateDeliverySlotMenuItemsRequest,
    current_admin = Depends(get_current_admin),
):
    """Admin override to update menu items for a specific delivery date."""
    try:
        updated_order = await order_service.update_delivery_slot_menu_items(
            order_id,
            actor_user_id=str(current_admin.id),
            delivery_date=payload.delivery_date,
            menu_items=payload.menu_items,
            notes=payload.notes,
            override_cutoff=payload.override_cutoff,
            actor_role="admin",
        )
        try:
            from app.api.v1.orders import order_to_response
            response_payload = order_to_response(updated_order)
        except Exception:
            response_payload = None

        return ApiResponse(
            success=True,
            data=response_payload,
            message="Delivery slot updated successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating delivery slot (admin): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update delivery slot",
        )

@router.delete("/delivery-zones/{zone_id}", response_model=ApiResponse[None])
async def delete_delivery_zone(
    zone_id: str,
    permanent: bool = Query(False),
    current_admin = Depends(get_current_admin)
):
    """Delete delivery zone"""
    try:
        from bson import ObjectId
        
        if delivery_service.zones is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delivery zones collection not available"
            )
        
        if not ObjectId.is_valid(zone_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid zone ID"
            )
        
        if permanent:
            result = await delivery_service.zones.delete_one({"_id": ObjectId(zone_id)})
            deleted = result.deleted_count
            matched = result.deleted_count
        else:
            result = await delivery_service.zones.update_one(
                {"_id": ObjectId(zone_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            deleted = result.modified_count
            matched = result.matched_count

        if (deleted or 0) == 0 and (matched or 0) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery zone not found"
            )
        
        return ApiResponse(
            success=True,
            message="Delivery zone deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting delivery zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete delivery zone: {str(e)}"
        )

# ============= WEEKLY MENU SCHEDULE =============

@router.post("/weekly-schedule", response_model=ApiResponse[dict])
async def create_weekly_schedule(
    delivery_date: str = Form(..., description="Delivery date (YYYY-MM-DD)"),
    menu_rotation: int = Form(..., ge=1, le=8, description="Menu rotation (1-8)"),
    menu_item_ids: str = Form(..., description="Menu item IDs (JSON array)"),
    current_admin = Depends(get_current_admin)
):
    """Create or update weekly menu schedule"""
    try:
        # Parse menu item IDs
        try:
            item_ids = json.loads(menu_item_ids)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid menu item IDs format")
        
        schedule = await menu_service.create_weekly_menu_schedule(
            delivery_date,
            menu_rotation,
            item_ids
        )
        
        return ApiResponse(
            success=True,
            data={"id": str(schedule.id)},
            message="Weekly schedule created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating weekly schedule: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create schedule: {str(e)}"
        )

# ============= STANDALONE IMAGE UPLOAD =============

@router.post("/upload-image", response_model=ApiResponse[dict])
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    folder: str = Form("general", description="Folder name for organization"),
    current_admin = Depends(get_current_admin)
):
    """Upload image to Cloudflare R2"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ValueError("File must be an image")
        
        # Read file content
        content = await file.read()
        
        # Upload to R2
        public_url = await r2_client.upload_file(
            content,
            file.filename,
            folder,
            file.content_type
        )
        
        return ApiResponse(
            success=True,
            data={"url": public_url},
            message="Image uploaded successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to upload image: {str(e)}"
        )

# ============= SALES REPORTS =============

@router.get("/sales-report", response_model=ApiResponse[dict])
async def get_sales_report(
    start_date: str,
    end_date: str,
    current_admin = Depends(get_current_admin)
):
    """Generate sales report"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        report = await admin_service.get_sales_report(start, end)
        
        return ApiResponse(
            success=True,
            data=report
        )
    except Exception as e:
        logger.error(f"Error generating sales report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to generate report: {str(e)}"
        )
