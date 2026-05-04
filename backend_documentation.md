# Backend Project Documentation
**Generated on:** 2025-11-13 20:04:56
**Project Root:** `D:\NexusNao\CLIENTS\BAKAR\backend`

---

## Table of Contents

- **Root/**
  - [Dockerfile](#dockerfile)
  - [PROJECT_DOCUMENTATION.md](#project_documentationmd)
  - [README.md](#readmemd)
- **app/**
  - [__init__.py](#app-__init__py)
- **app\api/**
  - [__init__.py](#app-api-__init__py)
- **app\api\v1/**
  - [__init__.py](#app-api-v1-__init__py)
  - [addresses.py](#app-api-v1-addressespy)
  - [admin.py](#app-api-v1-adminpy)
  - [auth.py](#app-api-v1-authpy)
  - [cart.py](#app-api-v1-cartpy)
  - [contact.py](#app-api-v1-contactpy)
  - [delivery.py](#app-api-v1-deliverypy)
  - [menu.py](#app-api-v1-menupy)
  - [notifications.py](#app-api-v1-notificationspy)
  - [orders.py](#app-api-v1-orderspy)
  - [payments.py](#app-api-v1-paymentspy)
- **app\config/**
  - [__init__.py](#app-config-__init__py)
  - [database.py](#app-config-databasepy)
  - [r2_client.py](#app-config-r2_clientpy)
  - [settings.py](#app-config-settingspy)
  - [stripe_client.py](#app-config-stripe_clientpy)
- **app/**
  - [main.py](#app-mainpy)
- **app\middleware/**
  - [__init__.py](#app-middleware-__init__py)
  - [auth_middleware.py](#app-middleware-auth_middlewarepy)
  - [error_handler.py](#app-middleware-error_handlerpy)
- **app\models/**
  - [__init__.py](#app-models-__init__py)
  - [catering.py](#app-models-cateringpy)
  - [delivery.py](#app-models-deliverypy)
  - [menu.py](#app-models-menupy)
  - [order.py](#app-models-orderpy)
  - [subscription.py](#app-models-subscriptionpy)
  - [user.py](#app-models-userpy)
- **app\schemas/**
  - [__init__.py](#app-schemas-__init__py)
  - [auth.py](#app-schemas-authpy)
  - [cart.py](#app-schemas-cartpy)
  - [contact.py](#app-schemas-contactpy)
  - [menu.py](#app-schemas-menupy)
  - [order.py](#app-schemas-orderpy)
  - [payment.py](#app-schemas-paymentpy)
  - [response.py](#app-schemas-responsepy)
  - [subscription.py](#app-schemas-subscriptionpy)
- **app\services/**
  - [__init__.py](#app-services-__init__py)
  - [admin_service.py](#app-services-admin_servicepy)
  - [auth_service.py](#app-services-auth_servicepy)
  - [cart_service.py](#app-services-cart_servicepy)
  - [delivery_service.py](#app-services-delivery_servicepy)
  - [email_service.py](#app-services-email_servicepy)
  - [menu_service.py](#app-services-menu_servicepy)
  - [notification_service.py](#app-services-notification_servicepy)
  - [order_service.py](#app-services-order_servicepy)
  - [payment_service.py](#app-services-payment_servicepy)
  - [reminder_service.py](#app-services-reminder_servicepy)
  - [subscription_service.py](#app-services-subscription_servicepy)
- **app\utils/**
  - [__init__.py](#app-utils-__init__py)
  - [constants.py](#app-utils-constantspy)
  - [default_delivery_zones.py](#app-utils-default_delivery_zonespy)
  - [helpers.py](#app-utils-helperspy)
  - [security.py](#app-utils-securitypy)
  - [validators.py](#app-utils-validatorspy)
- **Root/**
  - [docs.py](#docspy)
  - [requirements.txt](#requirementstxt)
- **scripts/**
  - [seed_delivery_zones.py](#scripts-seed_delivery_zonespy)
  - [seed_menu_items.py](#scripts-seed_menu_itemspy)

---

## File Contents

### 📁 Root

#### 📄 Dockerfile
**Path:** `Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

#### 📄 PROJECT_DOCUMENTATION.md
**Path:** `PROJECT_DOCUMENTATION.md`

```markdown

```

---

#### 📄 README.md
**Path:** `README.md`

```markdown
# Bakar's Food & Catering - Backend API

Production-ready FastAPI backend for Bakar's Food & Catering, a Sydney-based food delivery and catering business offering Daily Menu, Meal Subscriptions, and Special Catering services.

## 🚀 Features

- **Daily Menu Orders**: Same-day meal delivery within 6km radius
- **Meal Subscriptions**: Meal box subscriptions with flexible deal packages
- **Special Catering**: Event catering with per-head pricing
- **Sidelines System**: Universal add-ons across all order types
- **Stripe Payments**: Secure payment processing
- **WhatsApp Notifications**: Order confirmations and updates
- **Admin Dashboard**: Order management and analytics
- **Cloudflare R2 Storage**: Image hosting for menu items
- **Google Maps Integration**: Delivery validation and distance calculation

## 📋 Prerequisites

- Python 3.11+
- MongoDB Atlas account
- Stripe account
- Cloudflare R2 account
- WhatsApp Business API access
- Google Maps API key

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd backend
```
```

---

### 📁 app

#### 📄 __init__.py
**Path:** `app\__init__.py`

```python

```

---

### 📁 app\api

#### 📄 __init__.py
**Path:** `app\api\__init__.py`

```python

```

---

### 📁 app\api\v1

#### 📄 __init__.py
**Path:** `app\api\v1\__init__.py`

```python
from fastapi import APIRouter
from app.api.v1 import (
    addresses,
    admin,
    auth,
    cart,
    contact,
    delivery,
    menu,
    notifications,
    orders,
    payments,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(addresses.router)
api_router.include_router(menu.router)
api_router.include_router(delivery.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(admin.router)
api_router.include_router(notifications.router)
api_router.include_router(contact.router)
```

---

#### 📄 addresses.py
**Path:** `app\api\v1\addresses.py`

```python
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth_middleware import get_current_user
from app.schemas.auth import AddAddressRequest, AddressSchema, UpdateAddressRequest
from app.schemas.response import ApiResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("", response_model=ApiResponse[List[AddressSchema]])
async def list_addresses(current_user=Depends(get_current_user)):
    """List all addresses for the authenticated user."""
    try:
        addresses = await auth_service.list_addresses(str(current_user.id))
        return ApiResponse(success=True, data=addresses)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/{address_id}", response_model=ApiResponse[AddressSchema])
async def get_address(address_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific address."""
    try:
        address = await auth_service.get_address(str(current_user.id), address_id)
        return ApiResponse(success=True, data=address)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("", response_model=ApiResponse[AddressSchema])
async def create_address(
    payload: AddAddressRequest, current_user=Depends(get_current_user)
):
    """Create a new address for the authenticated user."""
    try:
        address = await auth_service.add_address(str(current_user.id), payload)
        return ApiResponse(
            success=True, data=address, message="Address added successfully"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add address",
        )


@router.put("/{address_id}", response_model=ApiResponse[AddressSchema])
async def update_address(
    address_id: str,
    payload: UpdateAddressRequest,
    current_user=Depends(get_current_user),
):
    """Update an existing address."""
    try:
        address = await auth_service.update_address(
            str(current_user.id), address_id, payload
        )
        return ApiResponse(
            success=True, data=address, message="Address updated successfully"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update address",
        )


@router.delete("/{address_id}", response_model=ApiResponse[None])
async def delete_address(address_id: str, current_user=Depends(get_current_user)):
    """Delete an address."""
    try:
        await auth_service.delete_address(str(current_user.id), address_id)
        return ApiResponse(success=True, message="Address deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete address",
        )


@router.put("/{address_id}/default", response_model=ApiResponse[AddressSchema])
async def set_default_address(address_id: str, current_user=Depends(get_current_user)):
    """Set an address as the default shipping address."""
    try:
        address = await auth_service.set_default_address(
            str(current_user.id), address_id
        )
        return ApiResponse(
            success=True, data=address, message="Default address updated successfully"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update default address",
        )
```

---

#### 📄 admin.py
**Path:** `app\api\v1\admin.py`

```python
from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from datetime import datetime
from typing import List, Optional
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
from app.config.r2_client import r2_client
from app.middleware.auth_middleware import get_current_admin
from app.schemas.order import UpdateOrderStatusRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

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
            date_to=date_to_obj
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
    image: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin)
):
    """Create menu item"""
    try:
        # Upload image if provided
        image_url = None
        if image:
            content = await image.read()
            image_url = await r2_client.upload_file(
                content,
                image.filename,
                "menu-items",
                image.content_type
            )
        
        # Parse allergens
        allergens_list = []
        if allergens:
            allergens_list = [a.strip() for a in allergens.split(',') if a.strip()]
        
        item_data = {
            "name": name,
            "category": category,
            "price": price,
            "description": description,
            "is_available_for_daily": is_available_for_daily,
            "is_available_for_meal_plan": is_available_for_meal_plan,
            "allergens": allergens_list,
            "spice_level": spice_level,
            "is_vegetarian": is_vegetarian,
            "is_halal": is_halal,
        }
        
        created_item = await menu_service.create_menu_item(item_data, image_url)
        
        return ApiResponse(
            success=True,
            data={
                "item": MenuItemResponse.from_model(created_item),
                "id": str(created_item.id),
            },
            message="Menu item created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating menu item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu item: {str(e)}"
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
        if spice_level is not None:
            update_data["spice_level"] = spice_level
        if is_vegetarian is not None:
            update_data["is_vegetarian"] = is_vegetarian
        if is_halal is not None:
            update_data["is_halal"] = is_halal
        if allergens is not None:
            update_data["allergens"] = [a.strip() for a in allergens.split(',') if a.strip()]
        
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
        else:
            result = await delivery_service.zones.update_one(
                {"_id": ObjectId(zone_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
        
        if result.deleted_count == 0 and result.matched_count == 0:
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
```

---

#### 📄 auth.py
**Path:** `app\api\v1\auth.py`

```python
from fastapi import APIRouter, HTTPException, status, Depends
from urllib.parse import quote_plus
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    AddAddressRequest,
    UpdateProfileRequest,
    RegistrationResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.schemas.response import ApiResponse
from app.services.auth_service import auth_service
from app.services.email_service import send_verification_email, send_password_reset_email
from app.middleware.auth_middleware import get_current_user
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[RegistrationResponse])
async def register(user_data: UserRegisterRequest):
    """Register a new user and send verification email"""
    try:
        user = await auth_service.register_user(user_data)
        
        # Generate verification code
        code = await auth_service.generate_verification_code(user.email)
        
        # Send verification email
        await send_verification_email(
            email=user.email,
            name=user.first_name,
            code=code
        )
        
        return ApiResponse(
            success=True,
            data=RegistrationResponse(
                email=user.email,
                message="Registration successful! Please check your email for verification code."
            ),
            message="Registration successful! Please verify your email."
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(login_data: UserLoginRequest):
    """Login user"""
    try:
        user, token = await auth_service.login_user(login_data)
        
        addresses = auth_service.format_addresses_for_response(
            user.addresses, str(user.id)
        )
        return ApiResponse(
            success=True,
            data=TokenResponse(
                access_token=token,
                user=UserResponse(
                    id=str(user.id),
                    email=user.email,
                    phone=user.phone,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    role=user.role,
                    addresses=addresses,
                    is_active=user.is_active,
                    email_verified=user.email_verified
                )
            ),
            message="Login successful"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.get("/profile", response_model=ApiResponse[UserResponse])
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    addresses = auth_service.format_addresses_for_response(
        current_user.addresses, str(current_user.id)
    )
    return ApiResponse(
        success=True,
        data=UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            phone=current_user.phone,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            role=current_user.role,
            addresses=addresses,
            is_active=current_user.is_active,
            email_verified=current_user.email_verified
        )
    )

@router.put("/profile", response_model=ApiResponse[UserResponse])
async def update_profile(
    update_data: UpdateProfileRequest,
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    try:
        update_dict = update_data.dict(exclude_unset=True)
        user = await auth_service.update_profile(str(current_user.id), update_dict)
        addresses = auth_service.format_addresses_for_response(
            user.addresses, str(user.id)
        )
        return ApiResponse(
            success=True,
            data=UserResponse(
                id=str(user.id),
                email=user.email,
                phone=user.phone,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                addresses=addresses,
                is_active=user.is_active,
                email_verified=user.email_verified
            ),
            message="Profile updated successfully"
        )
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Profile update failed")

@router.post("/addresses", response_model=ApiResponse[UserResponse])
async def add_address(
    address_data: AddAddressRequest,
    current_user = Depends(get_current_user)
):
    """Add new address"""
    try:
        await auth_service.add_address(str(current_user.id), address_data)
        user = await auth_service.get_user_by_id(str(current_user.id))
        if not user:
            raise ValueError("Failed to retrieve updated user")

        addresses = auth_service.format_addresses_for_response(
            user.addresses, str(user.id)
        )
        return ApiResponse(
            success=True,
            data=UserResponse(
                id=str(user.id),
                email=user.email,
                phone=user.phone,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                addresses=addresses,
                is_active=user.is_active,
                email_verified=user.email_verified
            ),
            message="Address added successfully"
        )
    except Exception as e:
        logger.error(f"Add address error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add address")

@router.post("/verify-email", response_model=ApiResponse[TokenResponse])
async def verify_email(verify_data: VerifyEmailRequest):
    """Verify email with verification code"""
    try:
        # Verify the code
        is_verified = await auth_service.verify_email_code(verify_data.email, verify_data.code)
        
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Get the verified user
        user = await auth_service.collection.find_one({"email": verify_data.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Create access token
        token = await auth_service.create_access_token(
            data={"sub": str(user["_id"]), "email": user["email"], "role": user["role"]}
        )
        
        # Get user model
        user = auth_service._normalize_user_document(user)
        from app.models.user import UserModel
        user_model = UserModel(**user)
        
        addresses = auth_service.format_addresses_for_response(
            user_model.addresses, str(user_model.id)
        )
        
        return ApiResponse(
            success=True,
            data=TokenResponse(
                access_token=token,
                user=UserResponse(
                    id=str(user_model.id),
                    email=user_model.email,
                    phone=user_model.phone,
                    first_name=user_model.first_name,
                    last_name=user_model.last_name,
                    role=user_model.role,
                    addresses=addresses,
                    is_active=user_model.is_active,
                    email_verified=user_model.email_verified
                )
            ),
            message="Email verified successfully!"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Verification failed")

@router.post("/resend-verification", response_model=ApiResponse[dict])
async def resend_verification(resend_data: ResendVerificationRequest):
    """Resend verification code"""
    try:
        # Generate new code
        code = await auth_service.resend_verification_code(resend_data.email)
        
        # Get user to send email
        user = await auth_service.collection.find_one({"email": resend_data.email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Send verification email
        await send_verification_email(
            email=resend_data.email,
            name=user["first_name"],
            code=code
        )
        
        return ApiResponse(
            success=True,
            data={"email": resend_data.email},
            message="Verification code sent successfully!"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resend verification code")

@router.post("/forgot-password", response_model=ApiResponse[dict])
async def forgot_password(payload: ForgotPasswordRequest):
    """Initiate password reset and send email with link."""
    try:
        token, user = await auth_service.create_password_reset_request(payload.email)
        message = "If an account exists for this email, a reset link has been sent."
        base_url = settings.FRONTEND_BASE_URL.rstrip("/")
        reset_link = f"{base_url}/reset-password?token={token}&email={quote_plus(payload.email)}"

        await send_password_reset_email(
            email=payload.email,
            name=user.first_name or user.email,
            reset_link=reset_link,
        )

        return ApiResponse(success=True, data={"message": message})
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Forgot password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process password reset request",
        )

@router.post("/reset-password", response_model=ApiResponse[dict])
async def reset_password(payload: ResetPasswordRequest):
    """Reset password using token and new password."""
    try:
        is_reset = await auth_service.reset_password_with_token(
            payload.email,
            payload.token,
            payload.password,
        )
        if not is_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset link. Please request a new one.",
            )

        return ApiResponse(
            success=True,
            data={"message": "Password updated successfully."},
            message="Password updated successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset password",
        )
```

---

#### 📄 cart.py
**Path:** `app\api\v1\cart.py`

```python
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
    current_user = Depends(get_current_user)
):
    """Remove item from cart"""
    try:
        summary = await cart_service.remove_from_cart(
            str(current_user.id),
            item_id,
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
```

---

#### 📄 contact.py
**Path:** `app\api\v1\contact.py`

```python
from fastapi import APIRouter, HTTPException, status

from app.schemas.contact import ContactMessage, ContactResponse
from app.services.email_service import (
    EmailNotConfiguredError,
    send_contact_email,
)

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a contact message",
)
async def submit_contact_form(payload: ContactMessage) -> ContactResponse:
    """
    Receive a contact form submission and forward it via email.
    """
    try:
        await send_contact_email(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            message=payload.message,
        )
    except EmailNotConfiguredError as config_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(config_error),
        ) from config_error
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send contact message.",
        ) from exc

    return ContactResponse(
        success=True,
        message="Message sent successfully! We will reach out soon.",
    )
```

---

#### 📄 delivery.py
**Path:** `app\api\v1\delivery.py`

```python
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
            # Weekly/Catering - Sydney-wide
            return ApiResponse(
                success=True,
                data=DeliveryCheckResponse(
                    available=True,
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
```

---

#### 📄 menu.py
**Path:** `app\api\v1\menu.py`

```python
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends, Query
from typing import List, Optional, Union
from app.schemas.menu import (
    MenuItemResponse, CategoryResponse,
    WeeklyMenuResponse, CateringPackageResponse,
    CreateMenuItemRequest, UpdateMenuItemRequest,
    PaginationMeta, PaginatedMenuItemsResponse,
)
from app.schemas.response import ApiResponse
from app.schemas.subscription import MealSubscriptionPlanResponse
from app.services.menu_service import menu_service
from app.services.subscription_service import meal_subscription_service
from app.config.r2_client import r2_client
from app.config.settings import settings
from app.middleware.auth_middleware import get_current_admin
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
async def get_weekly_menu(delivery_date: str):
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

        return ApiResponse(
            success=True,
            data=WeeklyMenuResponse(
                delivery_date=menu_data["delivery_date"],
                menu_rotation=menu_data["menu_rotation"],
                items=response_items
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
```

---

#### 📄 notifications.py
**Path:** `app\api\v1\notifications.py`

```python
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
```

---

#### 📄 orders.py
**Path:** `app\api\v1\orders.py`

```python
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from app.schemas.order import (
    CreateDailyOrderRequest, CreateMealSubscriptionOrderRequest, CreateCateringOrderRequest,
    OrderResponse, OrderListResponse, UpdateOrderStatusRequest, UpdateMealSubscriptionOrderRequest
)
from app.schemas.response import ApiResponse
from app.services.order_service import order_service
from app.services.auth_service import auth_service
from app.services.notification_service import notification_service
from app.middleware.auth_middleware import get_current_user
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])

def order_to_response(order) -> OrderResponse:
    """Convert order model to response schema"""
    # Some order types (e.g. pickup) legitimately do not have a delivery address.
    # When the field is missing we pass `None` instead of `{}` so Pydantic's
    # AddressSchema validator is not triggered with empty data.
    delivery_address = order.delivery_address or None

    # The order already has OrderItem objects with all fields as primitives
    return OrderResponse(
        id=str(order.id),
        order_number=order.order_number,
        order_type=order.order_type,
        status=order.status,
        payment_status=order.payment_status,
        items=order.items,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        delivery_method=order.delivery_method,
        delivery_address_id=getattr(order, "delivery_address_id", None),
        delivery_address=delivery_address,
        created_at=order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at),
        payment_intent_id=order.stripe_payment_intent_id,
        payment_method=order.payment_method,
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
        orders = await order_service.get_user_orders(str(current_user.id), skip, page_size)
        
        return ApiResponse(
            success=True,
            data=OrderListResponse(
                orders=[order_to_response(order) for order in orders],
                total=len(orders),
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
```

---

#### 📄 payments.py
**Path:** `app\api\v1\payments.py`

```python
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
    stripe_enabled = bool(settings.STRIPE_PUBLISHABLE_KEY)
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY if stripe_enabled else None

    return ApiResponse(
        success=True,
        data=PaymentConfigResponse(
            stripe_enabled=stripe_enabled,
            stripe_publishable_key=publishable_key,
            currency=settings.STRIPE_CURRENCY,
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
```

---

### 📁 app\config

#### 📄 __init__.py
**Path:** `app\config\__init__.py`

```python

```

---

#### 📄 database.py
**Path:** `app\config\database.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from app.config.settings import settings
import dns.resolver
import logging
import socket
import threading
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from pymongo import errors as pymongo_errors

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

database = Database()
_doh_cache: Dict[str, Dict[str, Any]] = {}
_doh_cache_lock = threading.Lock()
_doh_patch_lock = threading.Lock()
_doh_patch_applied = False

async def connect_to_mongo():
    """Connect to MongoDB with improved error handling and DNS fallbacks."""
    doh_override = False
    mongodb_uri = settings.MONGODB_URL or ""
    allow_doh_fallback = mongodb_uri.startswith("mongodb+srv://") and not settings.MONGODB_FORCE_DOH

    while True:
        try:
            if settings.MONGODB_DNS_SERVERS:
                logger.info("Custom DNS configuration enabled")
            elif settings.MONGODB_FORCE_DOH or doh_override:
                logger.info("Forcing DNS-over-HTTPS for MongoDB resolution")
            else:
                logger.info("Using system default DNS resolution")

            configure_dns_resolver(force_doh=settings.MONGODB_FORCE_DOH or doh_override)

            effective_uri = build_effective_mongo_uri(
                mongodb_uri,
                force_doh=settings.MONGODB_FORCE_DOH or doh_override,
            )

            database.client = AsyncIOMotorClient(
                effective_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            database.db = database.client[settings.MONGODB_DB_NAME]

            await database.client.admin.command("ping")
            logger.info("Connected to MongoDB: %s", settings.MONGODB_DB_NAME)
            await create_indexes()
            break

        except pymongo_errors.ConfigurationError as exc:
            if allow_doh_fallback and _looks_like_dns_failure(exc):
                logger.warning("MongoDB SRV lookup failed via system DNS: %s", exc)
                logger.info("Retrying MongoDB connection with DoH fallback enabled")
                doh_override = True
                allow_doh_fallback = False
                continue
            _log_connection_failure(exc)
            raise
        except Exception as exc:
            _log_connection_failure(exc)
            raise


def build_effective_mongo_uri(uri: str, force_doh: Optional[bool] = None) -> str:
    """Convert mongodb+srv URIs to standard ones using DoH when requested."""
    if not uri or not uri.startswith("mongodb+srv://"):
        return uri

    parsed = urlparse(uri)
    host = parsed.hostname
    if not host:
        return uri

    query_params = parse_qs(parsed.query, keep_blank_values=True)
    base_params = {key: values[-1] for key, values in query_params.items()}

    use_doh = settings.MONGODB_FORCE_DOH if force_doh is None else force_doh
    if not use_doh:
        logger.info("Using mongodb+srv:// with system DNS resolution")
        return uri

    auth = ""
    if parsed.username:
        auth += quote(parsed.username)
        if parsed.password:
            auth += f":{quote(parsed.password)}"
        auth += "@"

    try:
        srv_records = _doh_query(f"_mongodb._tcp.{host}", "SRV")
        if not srv_records:
            logger.warning("Could not resolve SRV records for %s via DoH, falling back to heuristics", host)
            raise RuntimeError("No SRV answers via DoH")

        hosts = []
        for record in srv_records:
            data = record.get("data", "")
            parts = data.split()
            if len(parts) != 4:
                continue
            _, _, port, target = parts
            cleaned_target = target.rstrip(".")
            hosts.append(f"{cleaned_target}:{port}".replace(" ", ""))

        if not hosts:
            raise RuntimeError(f"No usable SRV entries returned for {host}")

        txt_records = _doh_query(f"_mongodb._tcp.{host}", "TXT")
        txt_params = {}
        if txt_records:
            raw_txt = txt_records[0].get("data", "").strip('"')
            if raw_txt:
                for item in raw_txt.split("&"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        txt_params[key] = value

        merged_params = dict(base_params)
        merged_params.update(txt_params)

        netloc = f"{auth}{','.join(hosts)}"
        new_url = urlunparse(
            (
                "mongodb",
                netloc,
                parsed.path or "",
                parsed.params,
                urlencode(merged_params),
                parsed.fragment,
            )
        )
        logger.info("Using SRV-resolved MongoDB URI via DoH")
        return new_url
    except Exception as exc:
        logger.warning("Failed to build MongoDB URI via DoH: %s", exc)
        fallback_uri = _build_atlas_seedlist_uri(parsed, auth, base_params, host)
        if fallback_uri:
            logger.warning(
                "Falling back to heuristic Atlas seed list for %s. Consider adding a mongodb:// URI to your .env to avoid DNS entirely.",
                host,
            )
            return fallback_uri
        return uri

def configure_dns_resolver(force_doh: Optional[bool] = None):
    """Allow overriding DNS resolution strategy before creating the MongoDB client."""
    configured_custom = _apply_custom_nameservers()
    configured_doh = _apply_dns_over_https(force_doh=force_doh)
    
    if not configured_custom and not configured_doh:
        logger.info("No custom DNS configuration applied, using system defaults")

def _build_atlas_seedlist_uri(parsed, auth: str, base_params: Dict[str, Any], host: str) -> str:
    """Best-effort fallback to Atlas shard hostnames when DNS is unavailable."""
    seed_hosts = _guess_atlas_seedlist(host)
    if not seed_hosts:
        return ""

    params = dict(base_params)
    _ensure_tls_param(params)
    if settings.MONGODB_REPLICA_SET and "replicaSet" not in params:
        params["replicaSet"] = settings.MONGODB_REPLICA_SET

    netloc = f"{auth}{','.join(seed_hosts)}"
    return urlunparse(
        (
            "mongodb",
            netloc,
            parsed.path or "",
            parsed.params,
            urlencode(params),
            parsed.fragment,
        )
    )

def _ensure_tls_param(params: Dict[str, Any]) -> None:
    """Make sure TLS stays enabled when converting SRV -> standard URI."""
    lower_keys = {key.lower() for key in params.keys()}
    if "tls" not in lower_keys and "ssl" not in lower_keys:
        params["tls"] = "true"

def _guess_atlas_seedlist(host: str) -> List[str]:
    """Heuristically derive Atlas shard hostnames when SRV lookup is impossible."""
    if not host or not host.endswith(".mongodb.net"):
        return []

    prefix, _, domain = host.partition(".")
    if not prefix or not domain:
        return []

    # If the user already supplied a direct shard hostname, nothing to do.
    if "-shard-00-" in prefix:
        return []

    return [
        f"{prefix}-shard-00-0{i}.{domain}:27017"
        for i in range(3)
    ]

def _apply_custom_nameservers():
    """Apply custom DNS nameservers if configured."""
    if not settings.MONGODB_DNS_SERVERS:
        return False

    servers = [
        server.strip()
        for server in settings.MONGODB_DNS_SERVERS.split(",")
        if server.strip()
    ]
    if not servers:
        return False

    try:
        resolver = dns.resolver.Resolver(configure=False)  # ✅ Don't use system config
        resolver.nameservers = servers
        resolver.timeout = 5  # ✅ Add timeout
        resolver.lifetime = 10  # ✅ Add lifetime
        dns.resolver.default_resolver = resolver
        logger.info("Configured custom DNS servers for MongoDB resolution: %s", servers)
        return True
    except Exception as e:
        logger.error("Failed to configure custom DNS servers: %s", e)
        return False

def _apply_dns_over_https(force_doh: Optional[bool] = None):
    """Force DNS queries through HTTPS (helps when UDP/TCP port 53 is blocked)."""
    enable_doh = settings.MONGODB_FORCE_DOH if force_doh is None else force_doh
    if not enable_doh:
        return False

    suffixes = [
        suffix.strip().lower()
        for suffix in settings.MONGODB_DOH_DOMAINS.split(",")
        if suffix.strip()
    ]
    if not suffixes:
        return False

    endpoints = _get_doh_endpoints()

    global _doh_patch_applied
    with _doh_patch_lock:
        if _doh_patch_applied:
            return True

        original_getaddrinfo = socket.getaddrinfo

        def doh_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            if host and _should_handle_host(host, suffixes):
                try:
                    resolved_port = _normalize_port(port)
                    addresses = _doh_lookup(host)
                    if addresses:
                        return [
                            (
                                socket.AF_INET,
                                type or socket.SOCK_STREAM,
                                proto or 0,
                                "",
                                (addr, resolved_port),
                            )
                            for addr in addresses
                        ]
                except Exception as exc:
                    logger.warning(
                        "DNS-over-HTTPS lookup failed for %s: %s, falling back to system DNS",
                        host,
                        exc,
                    )

            return original_getaddrinfo(host, port, family, type, proto, flags)

        socket.getaddrinfo = doh_getaddrinfo
        _doh_patch_applied = True
        logger.info(
            "Enabled DNS-over-HTTPS fallback via %s for suffixes: %s",
            endpoints[0],
            suffixes,
        )
    return True

def _looks_like_dns_failure(exc: Exception) -> bool:
    """Heuristic check to decide if the exception is DNS related."""
    message = str(exc).lower()
    keywords = [
        "resolution lifetime expired",
        "dns operation timed out",
        "failed to resolve",
        "srv record lookup failed",
        "nodename nor servname provided",
        "name or service not known",
        "temporary failure in name resolution",
    ]
    return any(keyword in message for keyword in keywords)

def _log_connection_failure(exc: Exception) -> None:
    logger.error(f"Could not connect to MongoDB: {exc}")
    logger.error("Troubleshooting tips:")
    logger.error("1. Check MONGODB_URL in your .env file")
    logger.error("2. Ensure MONGODB_FORCE_DOH=false unless DoH is required")
    logger.error("3. Verify network connection")
    logger.error("4. Check MongoDB Atlas IP whitelist (if using Atlas)")
    logger.error("5. Try using a standard mongodb:// URI instead of mongodb+srv://")

def _should_handle_host(host: str, suffixes: List[str]) -> bool:
    host_lower = host.lower()
    return any(host_lower.endswith(suffix) for suffix in suffixes)

def _normalize_port(port: Any) -> int:
    if isinstance(port, int):
        return port
    if isinstance(port, str) and port.isdigit():
        return int(port)
    return 0

def _doh_lookup(host: str) -> List[str]:
    now = time.time()
    with _doh_cache_lock:
        cached = _doh_cache.get(host)
        if cached and cached["expires_at"] > now:
            return cached["addresses"]

    answers = _doh_query(host, "A")

    addresses = [
        answer.get("data")
        for answer in answers
        if answer.get("type") == 1 and answer.get("data")
    ]
    if not addresses:
        raise RuntimeError(f"No A records returned for {host}")

    ttl_values = [answer.get("TTL") for answer in answers if answer.get("TTL")]
    ttl = min(ttl_values) if ttl_values else 60
    expires_at = now + max(ttl, 30)

    with _doh_cache_lock:
        _doh_cache[host] = {
            "addresses": addresses,
            "expires_at": expires_at,
        }
    return addresses

def _doh_query(name: str, record_type: str) -> List[Dict[str, Any]]:
    """Query DNS over HTTPS with timeout, retries, and error handling."""
    params = {"name": name, "type": record_type}
    headers = {"accept": "application/dns-json"}
    endpoints = _get_doh_endpoints()
    last_error: Optional[Exception] = None

    for endpoint in endpoints:
        try:
            request_params = dict(params)
            if "cloudflare-dns.com" in endpoint and "ct" not in request_params:
                request_params["ct"] = "application/dns-json"
            response = requests.get(
                endpoint,
                params=request_params,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json()
            answers = payload.get("Answer", [])
            if answers:
                return answers
            logger.warning(
                "DoH query via %s returned no answers for %s (type %s)",
                endpoint,
                name,
                record_type,
            )
        except requests.exceptions.Timeout as exc:
            logger.error(
                "DoH query timeout via %s for %s (type %s)",
                endpoint,
                name,
                record_type,
            )
            last_error = exc
        except requests.exceptions.RequestException as exc:
            logger.error(
                "DoH query failed via %s for %s: %s",
                endpoint,
                name,
                exc,
            )
            last_error = exc

    message = (
        f"DNS-over-HTTPS query failed for {name} (type {record_type}) via endpoints: "
        + ", ".join(endpoints)
    )
    if last_error:
        raise RuntimeError(message) from last_error
    raise RuntimeError(message)

def _get_doh_endpoints() -> List[str]:
    raw = settings.MONGODB_DOH_ENDPOINT or ""
    endpoints = [endpoint.strip() for endpoint in raw.split(",") if endpoint.strip()]
    if endpoints:
        return endpoints
    return [
        "https://cloudflare-dns.com/dns-query",
        "https://dns.google/resolve",
    ]

async def close_mongo_connection():
    """Close MongoDB connection"""
    try:
        if database.client:
            database.client.close()
            logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Fixed: Use 'is not None' instead of boolean evaluation
        if database.db is None:
            logger.warning("Database not yet available for creating indexes")
            return
            
        db = database.db
        
        # Users indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("phone")
        
        # Menu items indexes
        await db.menu_items.create_index("category")
        await db.menu_items.create_index("is_available")
        
        # Orders indexes
        await db.orders.create_index("user_id")
        await db.orders.create_index("order_number", unique=True)
        await db.orders.create_index("status")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    if database.db is None:
        logger.warning("Database not connected yet")
    return database.db
```

---

#### 📄 r2_client.py
**Path:** `app\config\r2_client.py`

```python
import boto3
from botocore.client import Config
from app.config.settings import settings
import uuid
import logging
from typing import Optional
import mimetypes

logger = logging.getLogger(__name__)

class R2Client:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL

        # Only initialize if credentials are provided
        if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                    config=Config(signature_version='s3v4'),
                    region_name='auto'
                )
                logger.info("R2 client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize R2 client: {e}")
        else:
            logger.warning("R2 credentials not configured - file upload will not work")

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "general",
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to R2 and return public URL
        """
        if not self.s3_client:
            # Return a placeholder URL for development
            logger.warning("R2 not configured - returning placeholder URL")
            return f"https://placeholder.images.com/{folder}/{filename}"

        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            object_key = f"{folder}/{unique_filename}"

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Upload to R2 with public-read ACL if your bucket supports it
            # Note: R2 doesn't support ACLs like S3, so public access must be configured at bucket level
            extra_args = {
                'ContentType': content_type,
                # Add cache control for better performance
                'CacheControl': 'public, max-age=31536000'
            }

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content,
                **extra_args
            )

            # Return public URL using the configured public endpoint
            public_url = f"{self.public_url}/{object_key}"
            logger.info(f"File uploaded successfully: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"Error uploading file to R2: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")

    async def delete_file(self, file_url: str) -> bool:
        """Delete file from R2"""
        if not self.s3_client:
            logger.warning("R2 not configured - cannot delete file")
            return False

        try:
            # Extract object key from URL
            # Handle both old and new URL formats
            if self.public_url in file_url:
                object_key = file_url.replace(f"{self.public_url}/", "")
            else:
                # Try to extract from old format URLs
                parts = file_url.split('/')
                if len(parts) >= 2:
                    object_key = '/'.join(parts[-2:])  # folder/filename
                else:
                    logger.error(f"Cannot extract object key from URL: {file_url}")
                    return False

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )

            logger.info(f"File deleted successfully: {file_url}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file from R2: {e}")
            return False

    async def get_file_url(self, object_key: str) -> str:
        """Generate public URL for an object key"""
        if not self.public_url:
            return f"https://placeholder.images.com/{object_key}"
        return f"{self.public_url}/{object_key}"

r2_client = R2Client()
```

---

#### 📄 settings.py
**Path:** `app\config\settings.py`

```python
import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "bakars_food_catering")
    MONGODB_DNS_SERVERS: Optional[str] = os.getenv("MONGODB_DNS_SERVERS", "")
    MONGODB_FORCE_DOH: bool = os.getenv("MONGODB_FORCE_DOH", "false").lower() == "true"
    MONGODB_DOH_ENDPOINT: str = os.getenv(
        "MONGODB_DOH_ENDPOINT",
        "https://cloudflare-dns.com/dns-query,https://dns.google/resolve",
    )
    MONGODB_DOH_DOMAINS: str = os.getenv("MONGODB_DOH_DOMAINS", "mongodb.net")
    MONGODB_REPLICA_SET: str = os.getenv("MONGODB_REPLICA_SET", "")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    
    # Cloudflare R2
    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "bakars-food-images")
    R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")
    
    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_CURRENCY: str = os.getenv("STRIPE_CURRENCY", "AUD")
    
    # WhatsApp Business API
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY", "") or None
    
    # Business Location
    BUSINESS_LATITUDE: float = float(os.getenv("BUSINESS_LATITUDE", "-33.855853"))
    BUSINESS_LONGITUDE: float = float(os.getenv("BUSINESS_LONGITUDE", "150.994854"))
    BUSINESS_ADDRESS: str = os.getenv("BUSINESS_ADDRESS", "504-508 Woodville Rd, Guildford, NSW 2161")
    
    # SMTP / Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", ""))
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Bakar's Food & Catering")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    CONTACT_RECIPIENT_EMAIL: str = os.getenv("CONTACT_RECIPIENT_EMAIL", os.getenv("SMTP_FROM_EMAIL", ""))
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    ORDER_NOTIFICATIONS_EMAIL: str = os.getenv("ORDER_NOTIFICATIONS_EMAIL", "bakarfoods@gmail.com")
    
    # CORS - Hardcoded for simplicity
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Reminder scheduler
    ENABLE_REMINDER_SCHEDULER: bool = os.getenv("ENABLE_REMINDER_SCHEDULER", "true").lower() == "true"
    REMINDER_SCHEDULER_INTERVAL_SECONDS: int = int(os.getenv("REMINDER_SCHEDULER_INTERVAL_SECONDS", "1800"))
    PURGE_LEGACY_MEAL_PLANS: bool = os.getenv("PURGE_LEGACY_MEAL_PLANS", "false").lower() == "true"

# Create settings instance
settings = Settings()
```

---

#### 📄 stripe_client.py
**Path:** `app\config\stripe_client.py`

```python
import stripe
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Configure Stripe only if key is available
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    logger.info("Stripe client configured")
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
        if not settings.STRIPE_SECRET_KEY:
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
        if not settings.STRIPE_SECRET_KEY:
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
        if not settings.STRIPE_SECRET_KEY:
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
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
            logger.error("Stripe not fully configured")
            raise Exception("Webhook processing not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise Exception("Invalid signature")

stripe_client = StripeClient()
```

---

### 📁 app

#### 📄 main.py
**Path:** `app\main.py`

```python
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import logging

from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection
from app.api.v1 import api_router
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.services.reminder_service import reminder_service
from app.services.subscription_service import meal_subscription_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def reminder_scheduler_loop(app: FastAPI, interval_seconds: int):
    """Background loop that periodically processes due subscription reminders."""
    interval = max(60, interval_seconds)
    while True:
        try:
            processed = await reminder_service.process_due_reminders()
            if processed:
                logger.info("Reminder scheduler processed %d subscription(s)", processed)
            app.state.reminder_scheduler_last_run = datetime.utcnow()
            app.state.reminder_scheduler_last_result = processed
        except asyncio.CancelledError:
            logger.info("Reminder scheduler task cancelled")
            raise
        except Exception as exc:
            logger.error("Reminder scheduler error: %s", exc, exc_info=True)
            app.state.reminder_scheduler_last_error = str(exc)

        await asyncio.sleep(interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    reminder_task = None
    # Startup
    logger.info("Starting up application...")
    await connect_to_mongo()
    if settings.PURGE_LEGACY_MEAL_PLANS:
        deleted = await meal_subscription_service.purge_legacy_defaults()
        if deleted:
            logger.info("Purged %d legacy meal plans", deleted)
    if settings.ENABLE_REMINDER_SCHEDULER:
        interval = settings.REMINDER_SCHEDULER_INTERVAL_SECONDS
        logger.info("Starting reminder scheduler (interval=%ss)", interval)
        reminder_task = asyncio.create_task(reminder_scheduler_loop(app, interval))
        app.state.reminder_task = reminder_task
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if reminder_task:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass
    await close_mongo_connection()
    logger.info("Application shut down complete")

# Initialize FastAPI app
app = FastAPI(
    title="Bakar's Food & Catering API",
    description="Backend API for Bakar's Food & Catering - Daily Menu, Meal Subscriptions, and Special Catering",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

origins = [
    # Production domains
    "https://bakarsfood.com",
    "https://www.bakarsfood.com",
    "https://xwgoocsgkswwccs48ss80wcg.bakarsfood.com",

    # Staging environment
    "https://staging.bakarsfood.com",

    # Development (local)
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",

    # Optional: Vercel frontend (if still used)
    "https://bakar-frontend-s9uf.vercel.app",
]

# Configure CORS with explicit origins and settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["*"],
    max_age=3600,
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    reminder_state = {
        "enabled": settings.ENABLE_REMINDER_SCHEDULER,
        "interval_seconds": settings.REMINDER_SCHEDULER_INTERVAL_SECONDS,
        "last_run": getattr(app.state, "reminder_scheduler_last_run", None),
        "last_processed": getattr(app.state, "reminder_scheduler_last_result", None),
        "last_error": getattr(app.state, "reminder_scheduler_last_error", None),
    }
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "reminder_scheduler": reminder_state,
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - returns API information"""
    return {
        "name": "Bakar's Food & Catering API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/api/docs",
        "alternative_docs": "/api/redoc",
        "health_check": "/health",
        "api_endpoints": {
            "auth": "/api/v1/auth",
            "menu": "/api/v1/menu",
            "orders": "/api/v1/orders",
            "cart": "/api/v1/cart",
            "delivery": "/api/v1/delivery",
            "payments": "/api/v1/payments",
            "admin": "/api/v1/admin",
            "notifications": "/api/v1/notifications"
        }
    }

# API info endpoint
@app.get("/api", tags=["Root"])
async def api_info():
    """API info endpoint"""
    return {
        "message": "Bakar's Food & Catering API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "menu": "/api/v1/menu",
            "orders": "/api/v1/orders",
            "cart": "/api/v1/cart",
            "delivery": "/api/v1/delivery",
            "payments": "/api/v1/payments",
            "admin": "/api/v1/admin",
            "notifications": "/api/v1/notifications"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
```

---

### 📁 app\middleware

#### 📄 __init__.py
**Path:** `app\middleware\__init__.py`

```python

```

---

#### 📄 auth_middleware.py
**Path:** `app\middleware\auth_middleware.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from app.services.auth_service import auth_service
from typing import Optional

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user

async def get_current_admin(current_user = Depends(get_current_user)):
    """Verify current user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

# Optional auth (for public endpoints that can benefit from user context)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """Get current user if token provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except:
        return None
```

---

#### 📄 error_handler.py
**Path:** `app\middleware\error_handler.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "message": str(exc.detail)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "message": "Invalid input data",
            "details": errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )
```

---

### 📁 app\models

#### 📄 __init__.py
**Path:** `app\models\__init__.py`

```python

```

---

#### 📄 catering.py
**Path:** `app\models\catering.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class CateringOrderModel(BaseModel):
    """Catering order-specific data"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: PyObjectId  # Reference to main order
    user_id: PyObjectId
    
    # Event details
    event_date: datetime
    event_time: Optional[str] = None
    venue_address: str
    guest_count: int
    
    # Package details
    package_type: str  # basic, premium, diamond
    package_price_per_head: float
    
    # Selected items
    selected_items: Dict[str, List[str]] = {}  # {category: [item_ids]}
    
    # Pricing
    package_total: float
    delivery_fee: float
    advance_payment_amount: float
    remaining_payment_amount: float
    
    # Payment tracking
    advance_paid: bool = False
    advance_payment_date: Optional[datetime] = None
    final_paid: bool = False
    final_payment_date: Optional[datetime] = None
    
    # Quote
    quote_sent: bool = False
    quote_sent_at: Optional[datetime] = None
    quote_accepted: bool = False
    
    # Additional details
    special_requests: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

#### 📄 delivery.py
**Path:** `app\models\delivery.py`

```python
from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class DeliveryZoneModel(BaseModel):
    """Delivery zone definition with postcode based pricing."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    zone_label: Optional[str] = None  # e.g. Zone 1 (0-14 km)
    postcode: str
    suburbs: List[str] = Field(default_factory=list)
    state: str = "NSW"
    distance_from_business: Optional[float] = None  # in km
    base_delivery_fee: float = 10.0  # per delivery day
    express_delivery_fee: Optional[float] = None  # optional surcharge per day
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    order_types: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

#### 📄 menu.py
**Path:** `app\models\menu.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

class CategoryModel(BaseModel):
    """Food category model"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str  # rice, curry, bbq, sweets, drinks
    display_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MenuItemModel(BaseModel):
    """Menu item model"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    category: str  # rice, curry, bbq, sweets, drinks
    price: float
    image_url: Optional[str] = None
    is_available: bool = True
    is_available_for_daily: bool = True
    is_available_for_meal_plan: bool = False
    allergens: List[str] = []
    spice_level: Optional[str] = None  # mild, medium, hot
    is_vegetarian: bool = False
    is_vegan: bool = False  # ✅ ADD THIS FIELD
    is_halal: bool = True
    nutritional_info: Optional[Dict] = None  # ✅ ADD THIS FIELD
    serving_size: Optional[str] = None  # ✅ ADD THIS FIELD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class WeeklyMenuScheduleModel(BaseModel):
    """Weekly menu rotation schedule"""
    id: Optional[str] = Field(default=None, alias="_id")
    delivery_date: datetime  # Monday or Thursday
    menu_rotation: int  # 1-8 (8 rotations per month)
    menu_items: List[str] = []  # List of menu item IDs
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CateringPackageModel(BaseModel):
    """Catering package definition"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str  # basic, premium, diamond
    display_name: str
    price_per_head: float
    description: str
    rules: dict  # Package composition rules
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

#### 📄 order.py
**Path:** `app\models\order.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class OrderItem(BaseModel):
    """Order item"""
    item_id: str
    item_name: str
    category: str
    quantity: int
    price: float
    subtotal: float

class OrderModel(BaseModel):
    """Main order model"""
    id: Optional[str] = Field(default=None, alias="_id")
    order_number: str
    user_id: str  # Changed from PyObjectId to str
    order_type: str  # daily, weekly, catering
    status: str = "pending"  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    payment_status: str = "pending"  # pending, paid, failed, refunded, partially_paid
    
    # Order items
    items: List[OrderItem] = []
    
    # Pricing
    subtotal: float
    delivery_fee: float
    total_amount: float
    
    # Delivery details
    delivery_method: str  # standard, express, pickup
    delivery_address_id: Optional[str] = None
    delivery_address: Optional[dict] = None
    delivery_instructions: Optional[str] = None
    
    # Payment details
    stripe_payment_intent_id: Optional[str] = None
    payment_method: Optional[str] = None
    paid_amount: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    
    # Additional metadata
    notes: Optional[str] = None
    admin_notes: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

#### 📄 subscription.py
**Path:** `app\models\subscription.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.user import PyObjectId


class WeekSelectionRulesModel(BaseModel):
    """Rules describing how many weeks a customer can schedule within a cycle."""

    available_weeks: Optional[int] = Field(default=None, ge=1)
    required_weeks: Optional[int] = Field(default=None, ge=1)
    deliveries_per_week: Optional[int] = Field(default=None, ge=1)
    allow_partial_weeks: bool = False


class CustomerNotificationSettingsModel(BaseModel):
    """Optional messaging displayed to customers for a plan."""

    upsell_message: Optional[str] = None
    reminder_message: Optional[str] = None
    upsell_condition: str = "always"


class ReminderSettingsModel(BaseModel):
    """Reminder scheduling configuration for subscribers."""

    enabled: bool = False
    frequency_days: int = Field(default=7, ge=1)
    channel: str = "in_app"  # in_app, email, both
    threshold_unselected_boxes: Optional[int] = Field(default=None, ge=0)


class MealSubscriptionPlanModel(BaseModel):
    """Configurable meal subscription plan definition."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    code: str
    name: str
    tab: str  # regular, weekly, fortnight, monthly, custom
    description: Optional[str] = None
    short_description: Optional[str] = None
    included_meals: int = 0
    deliveries_per_cycle: int = 0
    weeks_in_cycle: int = 0
    boxes_per_delivery: int = 0
    max_boxes_per_meal: Optional[int] = None
    price_per_plan: float = 0.0
    price_per_box: Optional[float] = None
    allow_multiple: bool = True
    min_boxes_delivery: Optional[int] = None
    min_boxes_pickup: Optional[int] = None
    display_badge: Optional[str] = None
    display_order: int = 0
    extra_box_price: Optional[float] = None
    highlight: bool = False
    is_active: bool = True
    require_terms_ack: bool = False
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRulesModel] = None
    customer_notifications: Optional[CustomerNotificationSettingsModel] = None
    reminder_settings: Optional[ReminderSettingsModel] = None
    metadata: Optional[Dict[str, Any]] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    menu_item_ids_by_day: Dict[str, List[str]] = Field(default_factory=dict)
    menu_items_by_day: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MealPlanSelection(BaseModel):
    """Selected plan information stored with an order."""

    plan_id: str
    plan_code: str
    plan_name: str
    plan_tab: str
    quantity: int
    included_meals: int
    included_boxes: int
    deliveries_in_cycle: int
    weeks_in_cycle: int
    max_boxes_per_meal: Optional[int] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRulesModel] = None
    customer_notifications: Optional[CustomerNotificationSettingsModel] = None
    metadata: Optional[Dict[str, Any]] = None
    plan_price: float = 0.0
    discount_applied: float = 0.0


class DeliverySlotSelection(BaseModel):
    """Meal selections for a specific delivery date."""

    delivery_date: datetime
    menu_items: Dict[str, int]  # {menu_item_id: quantity}
    notes: Optional[str] = None


class MealSubscriptionModel(BaseModel):
    """Stored meal subscription order data."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: PyObjectId
    user_id: PyObjectId

    fulfilment_type: str  # delivery, pickup, mixed
    postal_code: Optional[str] = None
    plan_selections: List[MealPlanSelection] = []
    delivery_slots: List[DeliverySlotSelection] = []

    total_selected_boxes: int = 0
    total_included_boxes: int = 0
    extra_boxes: int = 0
    extra_boxes_price: float = 0.0

    delivery_days: int = 0
    delivery_fee_per_day: float = 0.0
    total_delivery_fee: float = 0.0
    express_delivery: bool = False
    delivery_fee_notes: Optional[str] = None

    reminder_settings: Optional[ReminderSettingsModel] = None
    next_reminder_at: Optional[datetime] = None
    reminders_sent: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

#### 📄 user.py
**Path:** `app\models\user.py`

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(str):
    """Custom Pydantic type for MongoDB ObjectId"""
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                )
            ],
            serialization=core_schema.str_schema(),  # Fixed serialization
        )
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

class Address(BaseModel):
    """Address model"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    label: str
    street: str
    suburb: str
    postcode: str
    state: str = "NSW"
    country: str = "Australia"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    delivery_instructions: Optional[str] = None
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like getter for compatibility with legacy code paths."""
        if key == "_id":
            key = "id"
        return getattr(self, key, default)

class UserModel(BaseModel):
    """User MongoDB document model"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    phone: str
    password_hash: str
    first_name: str
    last_name: str
    role: str = "customer"  # customer or admin
    addresses: List[Address] = []
    is_active: bool = True
    email_verified: bool = False  # Email verification status
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class VerificationCode(BaseModel):
    """Email verification code model"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    code: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

---

### 📁 app\schemas

#### 📄 __init__.py
**Path:** `app\schemas\__init__.py`

```python

```

---

#### 📄 auth.py
**Path:** `app\schemas\auth.py`

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from app.utils.validators import validate_phone, validate_password_strength

class AddressSchema(BaseModel):
    """Address schema for responses"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    label: str
    street: str
    suburb: str
    postcode: str
    state: str = "NSW"
    country: str = "Australia"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    delivery_instructions: Optional[str] = None
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        populate_by_name = True

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _coerce_datetime_to_str(cls, value):
        """Ensure timestamp fields serialize as ISO strings."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    phone: str
    password: str
    first_name: str
    last_name: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not validate_phone(v):
            raise ValueError('Invalid Australian phone number')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    phone: str
    first_name: str
    last_name: str
    role: str
    addresses: List[Any] = []  # Allow any format for addresses
    is_active: bool
    email_verified: bool = False

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class RegistrationResponse(BaseModel):
    """Registration response (without token, requires verification)"""
    email: str
    message: str

class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    email: EmailStr
    code: str

class ResendVerificationRequest(BaseModel):
    """Resend verification code request"""
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    email: EmailStr
    token: str
    password: str
    confirm_password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        password = info.data.get('password')
        if password and v != password:
            raise ValueError('Passwords do not match')
        return v

class AddAddressRequest(BaseModel):
    """Add address request"""
    label: str
    street: str
    suburb: str
    postcode: str
    state: str = "NSW"
    country: str = "Australia"
    delivery_instructions: Optional[str] = None
    is_default: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UpdateAddressRequest(BaseModel):
    """Update address request"""
    label: Optional[str] = None
    street: Optional[str] = None
    suburb: Optional[str] = None
    postcode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    delivery_instructions: Optional[str] = None
    is_default: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if v and not validate_phone(v):
            raise ValueError('Invalid Australian phone number')
        return v
```

---

#### 📄 cart.py
**Path:** `app\schemas\cart.py`

```python
from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    """Cart item"""
    item_id: str
    item_name: str
    category: str
    quantity: int
    price: float
    subtotal: float

class CartSummary(BaseModel):
    """Cart summary"""
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    items_count: int

class AddToCartRequest(BaseModel):
    """Add to cart request"""
    item_id: str
    quantity: int = 1

class UpdateCartItemRequest(BaseModel):
    """Update cart item request"""
    quantity: int
```

---

#### 📄 contact.py
**Path:** `app\schemas\contact.py`

```python
from pydantic import BaseModel, EmailStr, Field


class ContactMessage(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str = Field(..., max_length=30)
    message: str = Field(..., max_length=2000)


class ContactResponse(BaseModel):
    success: bool = True
    message: str = "Thank you! Your message has been sent."
```

---

#### 📄 menu.py
**Path:** `app\schemas\menu.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryResponse(BaseModel):
    """Category response"""
    id: str
    _id: str
    name: str
    display_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    sort_order: int

    @classmethod
    def from_model(cls, category):
        """Convert CategoryModel to CategoryResponse"""
        return cls(
            id=str(category.id),
            _id=str(category.id),
            name=category.name,
            display_name=category.display_name,
            description=category.description,
            image_url=category.image_url,
            is_active=category.is_active,
            sort_order=category.sort_order
        )

class MenuItemResponse(BaseModel):
    """Menu item response"""
    id: str
    _id: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    image_url: Optional[str] = None
    is_available: bool
    is_available_for_daily: bool
    is_available_for_meal_plan: bool
    allergens: List[str] = []
    spice_level: Optional[str] = None
    is_vegetarian: bool
    is_vegan: bool = False
    is_halal: bool
    nutritional_info: Optional[dict] = None
    serving_size: Optional[str] = None
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, item):
        """Convert MenuItemModel to MenuItemResponse"""
        created_at_str = item.created_at.isoformat() if isinstance(item.created_at, datetime) else str(item.created_at)
        updated_at_str = item.updated_at.isoformat() if isinstance(item.updated_at, datetime) else str(item.updated_at)
        
        return cls(
            id=str(item.id),
            _id=str(item.id),
            name=item.name,
            description=item.description,
            category=item.category,
            price=item.price,
            image_url=item.image_url,
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
            created_at=created_at_str,
            updated_at=updated_at_str
        )

class WeeklyMenuResponse(BaseModel):
    """Weekly menu response"""
    delivery_date: str
    menu_rotation: int
    items: List[MenuItemResponse]

class CateringPackageResponse(BaseModel):
    """Catering package response"""
    id: str
    name: str
    display_name: str
    price_per_head: float
    description: str
    rules: dict

class PaginationMeta(BaseModel):
    """Generic pagination metadata"""
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PaginatedMenuItemsResponse(BaseModel):
    """Daily menu response with pagination details"""
    items: List[MenuItemResponse]
    pagination: PaginationMeta

# Request models
class CreateMenuItemRequest(BaseModel):
    """Create menu item request"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    is_available_for_daily: bool = True
    is_available_for_meal_plan: bool = False
    allergens: List[str] = []
    spice_level: Optional[str] = Field(None, pattern="^(mild|medium|hot)$")
    is_vegetarian: bool = False
    is_halal: bool = True

class UpdateMenuItemRequest(BaseModel):
    """Update menu item request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_available_for_daily: Optional[bool] = None
    is_available_for_meal_plan: Optional[bool] = None
    allergens: Optional[List[str]] = None
    spice_level: Optional[str] = Field(None, pattern="^(mild|medium|hot)$")
    is_vegetarian: Optional[bool] = None
    is_halal: Optional[bool] = None
```

---

#### 📄 order.py
**Path:** `app\schemas\order.py`

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.auth import AddressSchema
from app.models.order import OrderItem  # Import OrderItem from models
from app.schemas.subscription import PlanSelectionPayload, DeliverySlotPayload

class DailyOrderItemPayload(BaseModel):
    """Daily menu item payload."""
    item_id: str = Field(..., description="Menu item identifier")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class CreateDailyOrderRequest(BaseModel):
    """Create daily order request"""
    items: List[DailyOrderItemPayload]
    delivery_method: str  # standard, pickup
    delivery_address_id: Optional[str] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    payment_method: str = "cash"

class CreateMealSubscriptionOrderRequest(BaseModel):
    """Create meal subscription order request"""
    plan_selections: List[PlanSelectionPayload]
    delivery_slots: List[DeliverySlotPayload]
    delivery_address_id: Optional[str] = None
    fulfilment_method: str = "delivery"  # delivery, pickup
    is_express: bool = False
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    payment_method: str = "cash"

    @validator("plan_selections")
    def validate_plans(cls, value: List[PlanSelectionPayload]) -> List[PlanSelectionPayload]:
        if not value:
            raise ValueError("At least one meal plan selection is required")
        return value

    @validator("delivery_slots")
    def validate_slots(cls, value: List[DeliverySlotPayload]) -> List[DeliverySlotPayload]:
        if not value:
            raise ValueError("Delivery slots are required")
        return value

class CreateCateringOrderRequest(BaseModel):
    """Create catering order request"""
    package_type: str  # basic, premium, diamond
    guest_count: int
    event_date: str  # YYYY-MM-DD
    event_time: Optional[str] = None
    venue_address: str
    selected_items: Dict[str, List[str]]  # {category: [item_ids]}
    special_requests: Optional[str] = None
    payment_method: str = "cash"
    
    @validator('guest_count')
    def validate_guest_count(cls, v):
        if v < 10:
            raise ValueError('Minimum 10 guests required for catering')
        return v

class UpdateMealSubscriptionOrderRequest(CreateMealSubscriptionOrderRequest):
    """Update meal subscription order request"""
    pass


class OrderResponse(BaseModel):
    """Order response"""
    id: str
    order_number: str
    order_type: str
    status: str
    payment_status: str
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    total_amount: float
    delivery_method: str
    delivery_address_id: Optional[str] = None
    delivery_address: Optional[AddressSchema] = None
    created_at: str
    payment_intent_id: Optional[str] = None
    payment_method: Optional[str] = None

class OrderListResponse(BaseModel):
    """Order list response"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int

class UpdateOrderStatusRequest(BaseModel):
    """Update order status request"""
    status: str  # confirmed, preparing, out_for_delivery, delivered, cancelled
    admin_notes: Optional[str] = None
```

---

#### 📄 payment.py
**Path:** `app\schemas\payment.py`

```python
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
```

---

#### 📄 response.py
**Path:** `app\schemas\response.py`

```python
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

class DeliveryCheckResponse(BaseModel):
    """Delivery availability check response"""
    available: bool
    distance_km: Optional[float] = None
    delivery_fee: Optional[float] = None
    suburb: Optional[str] = None
    postcode: Optional[str] = None
    message: Optional[str] = None

class RevenueDaySummary(BaseModel):
    label: str
    date: str
    total: float


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_orders: int = 0
    total_orders_growth_percent: float = 0.0
    pending_orders: int = 0
    pending_orders_weekly_change_percent: float = 0.0
    confirmed_orders: int = 0
    preparing_orders: int = 0
    out_for_delivery_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    today_revenue: float = 0.0
    today_vs_yesterday_percent: float = 0.0
    weekly_revenue: float = 0.0
    weekly_growth_percent: float = 0.0
    monthly_revenue: float = 0.0
    monthly_growth_percent: float = 0.0
    total_revenue: float = 0.0
    total_revenue_growth_percent: float = 0.0
    weekly_revenue_breakdown: list[RevenueDaySummary] = []
    active_subscriptions: int = 0
    upcoming_catering_events: int = 0
```

---

#### 📄 subscription.py
**Path:** `app\schemas\subscription.py`

```python
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator, model_validator

from app.schemas.menu import MenuItemResponse

VALID_DELIVERY_DAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


class WeekSelectionRules(BaseModel):
    available_weeks: Optional[int] = Field(default=None, ge=1, le=12)
    required_weeks: Optional[int] = Field(default=None, ge=1, le=12)
    deliveries_per_week: Optional[int] = Field(default=None, ge=1, le=14)
    allow_partial_weeks: bool = False

    @model_validator(mode="after")
    def validate_week_window(cls, values: "WeekSelectionRules") -> "WeekSelectionRules":
        available = values.available_weeks
        required = values.required_weeks
        if available is not None and required is not None and required > available:
            raise ValueError(
                "required_weeks cannot be greater than available_weeks"
            )
        return values


class CustomerNotificationSettings(BaseModel):
    upsell_message: Optional[str] = None
    reminder_message: Optional[str] = None
    upsell_condition: Optional[str] = Field(
        default="always", description="always, when_plan_selected, when_no_plan, hidden"
    )

    @validator("upsell_condition", pre=True, always=True)
    def normalize_condition(cls, value: Optional[str]) -> str:
        default_value = "always"
        if not value:
            return default_value
        normalized = value.strip().lower()
        allowed = {"always", "when_plan_selected", "when_no_plan", "hidden"}
        if normalized not in allowed:
            return default_value
        return normalized


class ReminderSettings(BaseModel):
    enabled: bool = False
    frequency_days: int = Field(default=7, ge=1, le=30)
    channel: str = Field(default="in_app")  # in_app, email, both
    threshold_unselected_boxes: Optional[int] = Field(default=None, ge=0)


class MealSubscriptionPlanBase(BaseModel):
    code: str
    name: str
    tab: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    included_meals: int = 0
    deliveries_per_cycle: int = 0
    weeks_in_cycle: int = 0
    boxes_per_delivery: int = 0
    max_boxes_per_meal: Optional[int] = None
    price_per_plan: float = 0.0
    price_per_box: Optional[float] = None
    allow_multiple: bool = True
    min_boxes_delivery: Optional[int] = None
    min_boxes_pickup: Optional[int] = None
    display_badge: Optional[str] = None
    display_order: int = 0
    extra_box_price: Optional[float] = None
    highlight: bool = False
    require_terms_ack: bool = False
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: List[str] = Field(default_factory=list)
    week_selection_rules: Optional[WeekSelectionRules] = None
    customer_notifications: Optional[CustomerNotificationSettings] = None
    reminder_settings: Optional[ReminderSettings] = None
    metadata: Optional[Dict[str, Any]] = None
    available_delivery_days: List[str] = Field(default_factory=list)
    menu_item_ids_by_day: Dict[str, List[str]] = Field(default_factory=dict)

    @validator("code")
    def normalize_code(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    @validator("tab")
    def normalize_tab(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed_tabs = {
            "regular",
            "weekly",
            "fortnight",
            "monthly",
            "custom",
        }
        if normalized not in allowed_tabs:
            raise ValueError(
                f"Invalid tab '{value}'. Must be one of: {', '.join(sorted(allowed_tabs))}"
            )
        return normalized

    @validator("available_delivery_days", each_item=True, pre=True)
    def normalize_available_days(cls, value: str) -> str:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in VALID_DELIVERY_DAYS:
            raise ValueError(f"Invalid delivery day: {value}")
        return normalized

    @validator("menu_item_ids_by_day", pre=True, always=True)
    def normalize_menu_day_mapping(
        cls, value: Optional[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        if value is None:
            return {}
        normalized: Dict[str, List[str]] = {}
        for raw_day, items in value.items():
            if raw_day is None:
                continue
            day = str(raw_day).strip().lower()
            if day not in VALID_DELIVERY_DAYS:
                raise ValueError(
                    f"Invalid delivery day provided for menu mapping: {raw_day}"
                )
            if items is None:
                normalized[day] = []
                continue
            if not isinstance(items, list):
                raise ValueError("Menu items mapping must be a list of item IDs")
            normalized[day] = [str(item_id) for item_id in items if item_id is not None]
        return normalized

    @validator("terms_and_conditions", each_item=True, pre=True)
    def normalize_terms(cls, value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = value.strip()
        return normalized


class CreateMealSubscriptionPlanRequest(MealSubscriptionPlanBase):
    is_active: bool = True


class UpdateMealSubscriptionPlanRequest(BaseModel):
    name: Optional[str] = None
    tab: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    included_meals: Optional[int] = None
    deliveries_per_cycle: Optional[int] = None
    weeks_in_cycle: Optional[int] = None
    boxes_per_delivery: Optional[int] = None
    max_boxes_per_meal: Optional[int] = None
    price_per_plan: Optional[float] = None
    price_per_box: Optional[float] = None
    allow_multiple: Optional[bool] = None
    min_boxes_delivery: Optional[int] = None
    min_boxes_pickup: Optional[int] = None
    display_badge: Optional[str] = None
    display_order: Optional[int] = None
    extra_box_price: Optional[float] = None
    highlight: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    require_terms_ack: Optional[bool] = None
    acknowledgement_label: Optional[str] = None
    terms_and_conditions: Optional[List[str]] = None
    week_selection_rules: Optional[WeekSelectionRules] = None
    customer_notifications: Optional[CustomerNotificationSettings] = None
    reminder_settings: Optional[ReminderSettings] = None


class MealSubscriptionPlanResponse(MealSubscriptionPlanBase):
    id: str = Field(alias="_id")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    menu_items_by_day: Dict[str, List[MenuItemResponse]] = Field(default_factory=dict)


class MealSubscriptionPlanGroupedResponse(BaseModel):
    tab: str
    plans: List[MealSubscriptionPlanResponse]


class DeliveryZoneBase(BaseModel):
    postcode: str
    zone_label: Optional[str] = None
    suburbs: List[str] = Field(default_factory=list)
    state: str = "NSW"
    distance_from_business: Optional[float] = None
    base_delivery_fee: float = 10.0
    express_delivery_fee: Optional[float] = None
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True
    order_types: List[str] = Field(default_factory=list)


class CreateDeliveryZoneRequest(DeliveryZoneBase):
    pass


class UpdateDeliveryZoneRequest(BaseModel):
    zone_label: Optional[str] = None
    suburbs: Optional[List[str]] = None
    state: Optional[str] = None
    distance_from_business: Optional[float] = None
    base_delivery_fee: Optional[float] = None
    express_delivery_fee: Optional[float] = None
    max_delivery_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    order_types: Optional[List[str]] = None


class DeliveryZoneResponse(DeliveryZoneBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

class MealPlanListResponse(BaseModel):
    plans: List[MealSubscriptionPlanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlanSelectionPayload(BaseModel):
    plan_id: str
    quantity: int = Field(ge=1)


class DeliverySlotPayload(BaseModel):
    delivery_date: str  # ISO date
    menu_items: Dict[str, int]
    notes: Optional[str] = None

    @validator("delivery_date")
    def validate_delivery_date(cls, value: str) -> str:
        if not value:
            raise ValueError("delivery_date is required")
        return value

    @validator("menu_items")
    def validate_menu_items(cls, value: Dict[str, int]) -> Dict[str, int]:
        if not value:
            raise ValueError("menu_items must include at least one item")
        return value
```

---

### 📁 app\services

#### 📄 __init__.py
**Path:** `app\services\__init__.py`

```python

```

---

#### 📄 admin_service.py
**Path:** `app\services\admin_service.py`

```python
from typing import Dict, List
from datetime import datetime, timedelta
from app.config.database import get_database
from app.utils.constants import OrderStatus, PaymentStatus
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self):
        self._db = None
        self._orders = None
        self._users = None
        self._meal_subs = None
        self._legacy_weekly_subs = None
        self._catering_orders = None
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def orders(self):
        """Get orders collection lazily"""
        if self._orders is None and self.db is not None:
            self._orders = self.db.orders
        return self._orders
    
    @property
    def users(self):
        """Get users collection lazily"""
        if self._users is None and self.db is not None:
            self._users = self.db.users
        return self._users
    
    @property
    def meal_subs(self):
        """Get meal_subscriptions collection lazily"""
        if self._meal_subs is None and self.db is not None:
            self._meal_subs = self.db.meal_subscriptions
        return self._meal_subs
    
    @property
    def weekly_subs_legacy(self):
        """Access legacy weekly_subscriptions collection if it exists."""
        if self._legacy_weekly_subs is None and self.db is not None:
            self._legacy_weekly_subs = getattr(self.db, "weekly_subscriptions", None)
        return self._legacy_weekly_subs
    
    @property
    def catering_orders(self):
        """Get catering_orders collection lazily"""
        if self._catering_orders is None and self.db is not None:
            self._catering_orders = self.db.catering_orders
        return self._catering_orders

    @staticmethod
    def _calculate_growth(current: float, previous: float) -> float:
        """Calculate percentage growth between current and previous values."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    @staticmethod
    def _serialize_datetime(value):
        """Convert datetime-like values to ISO strings for API responses."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _normalize_address(address: Dict) -> Dict:
        """Ensure delivery address fields are serializable for responses."""
        if not address:
            return None

        normalized = dict(address)
        for key in ("_id", "id", "user_id"):
            if normalized.get(key) is not None:
                normalized[key] = str(normalized[key])

        for key in ("created_at", "updated_at"):
            if key in normalized:
                normalized[key] = AdminService._serialize_datetime(normalized.get(key))
        return normalized

    @staticmethod
    def _map_order_type(order_type: str) -> str:
        """Align backend order types with admin frontend expectations."""
        mapping = {
            "daily": "daily_menu",
            "daily_menu": "daily_menu",
            "weekly": "meal_subscription",
            "subscription": "meal_subscription",
            "meal_subscription": "meal_subscription",
            "catering": "special_catering",
            "special_catering": "special_catering",
        }
        return mapping.get(order_type, order_type)
    
    async def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics with real-time data"""
        try:
            if self.orders is None:
                logger.warning("Orders collection not available")
                return self._get_empty_stats()

            # ✅ FIX: Use local time instead of UTC for better date accuracy
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day)
            today_end = today_start + timedelta(days=1)
            yesterday_start = today_start - timedelta(days=1)
            yesterday_end = today_start

            # Get current week boundaries (Monday to Sunday)
            week_start_dt = now - timedelta(days=now.weekday())
            week_start = datetime(week_start_dt.year, week_start_dt.month, week_start_dt.day)
            week_end = week_start + timedelta(days=7)
            prev_week_start = week_start - timedelta(days=7)
            prev_week_end = week_start

            # Get current month boundaries
            month_start = datetime(now.year, now.month, 1)
            if month_start.month == 12:
                next_month_start = datetime(month_start.year + 1, 1, 1)
            else:
                next_month_start = datetime(month_start.year, month_start.month + 1, 1)
            if month_start.month == 1:
                prev_month_start = datetime(month_start.year - 1, 12, 1)
            else:
                prev_month_start = datetime(month_start.year, month_start.month - 1, 1)
            prev_month_end = month_start

            logger.info(f"📊 Calculating dashboard stats for {now.strftime('%Y-%m-%d %H:%M')}")
            logger.info(f"   Today: {today_start.strftime('%Y-%m-%d')} to {today_end.strftime('%Y-%m-%d')}")
            logger.info(f"   This week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")

            # ✅ FIX: Count ALL orders (not just paid ones) for total orders
            total_orders = await self.orders.count_documents({})
            logger.info(f"   Total orders in DB: {total_orders}")

            # Current month vs previous month orders (for growth)
            current_month_orders = await self.orders.count_documents({
                "created_at": {"$gte": month_start, "$lt": next_month_start}
            })
            previous_month_orders = await self.orders.count_documents({
                "created_at": {"$gte": prev_month_start, "$lt": prev_month_end}
            })
            total_orders_growth_percent = self._calculate_growth(
                current_month_orders, previous_month_orders
            )

            logger.info(f"   Orders this month: {current_month_orders}, last month: {previous_month_orders}")

            # ✅ FIX: Count pending orders (pending, confirmed, preparing)
            pending_statuses = [
                OrderStatus.PENDING.value,
                OrderStatus.CONFIRMED.value,
                OrderStatus.PREPARING.value,
            ]
            pending_orders = await self.orders.count_documents({
                "status": {"$in": pending_statuses}
            })

            # Pending orders this week vs last week
            pending_orders_this_week = await self.orders.count_documents({
                "status": {"$in": pending_statuses},
                "created_at": {"$gte": week_start, "$lt": week_end}
            })
            pending_orders_last_week = await self.orders.count_documents({
                "status": {"$in": pending_statuses},
                "created_at": {"$gte": prev_week_start, "$lt": prev_week_end}
            })
            pending_orders_weekly_change_percent = self._calculate_growth(
                pending_orders_this_week, pending_orders_last_week
            )

            logger.info(f"   Pending orders: {pending_orders} (this week: {pending_orders_this_week})")

            # Status breakdown
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_results = await self.orders.aggregate(status_pipeline).to_list(None)
            status_counts = {res["_id"]: res["count"] for res in status_results}

            confirmed_orders = status_counts.get(OrderStatus.CONFIRMED.value, 0)
            preparing_orders = status_counts.get(OrderStatus.PREPARING.value, 0)
            out_for_delivery_orders = status_counts.get(OrderStatus.OUT_FOR_DELIVERY.value, 0)
            completed_orders = status_counts.get(OrderStatus.DELIVERED.value, 0)
            cancelled_orders = status_counts.get(OrderStatus.CANCELLED.value, 0)

            # ✅ FIX: Include BOTH paid AND pending orders in revenue (since pending will be paid)
            revenue_statuses = [PaymentStatus.PAID.value, PaymentStatus.PENDING.value]

            # Today's revenue
            today_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": today_start, "$lt": today_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            today_result = await self.orders.aggregate(today_pipeline).to_list(1)
            today_revenue = today_result[0]["total"] if today_result else 0.0

            # Yesterday's revenue
            yesterday_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": yesterday_start, "$lt": yesterday_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            yesterday_result = await self.orders.aggregate(yesterday_pipeline).to_list(1)
            yesterday_revenue = yesterday_result[0]["total"] if yesterday_result else 0.0
            today_vs_yesterday_percent = self._calculate_growth(today_revenue, yesterday_revenue)

            logger.info(f"   Today's revenue: ${today_revenue:.2f}, yesterday: ${yesterday_revenue:.2f}")

            # Weekly revenue
            weekly_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": week_start, "$lt": week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            weekly_result = await self.orders.aggregate(weekly_pipeline).to_list(1)
            weekly_revenue = weekly_result[0]["total"] if weekly_result else 0.0

            # Previous week revenue
            previous_week_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": prev_week_start, "$lt": prev_week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            previous_week_result = await self.orders.aggregate(previous_week_pipeline).to_list(1)
            previous_week_revenue = previous_week_result[0]["total"] if previous_week_result else 0.0
            weekly_growth_percent = self._calculate_growth(weekly_revenue, previous_week_revenue)

            logger.info(f"   Weekly revenue: ${weekly_revenue:.2f}, last week: ${previous_week_revenue:.2f}")

            # Monthly revenue
            monthly_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": month_start, "$lt": next_month_start},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            monthly_result = await self.orders.aggregate(monthly_pipeline).to_list(1)
            monthly_revenue = monthly_result[0]["total"] if monthly_result else 0.0

            # Previous month revenue
            previous_month_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": prev_month_start, "$lt": prev_month_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            previous_month_result = await self.orders.aggregate(previous_month_pipeline).to_list(1)
            previous_month_revenue = previous_month_result[0]["total"] if previous_month_result else 0.0
            monthly_growth_percent = self._calculate_growth(monthly_revenue, previous_month_revenue)

            logger.info(f"   Monthly revenue: ${monthly_revenue:.2f}, last month: ${previous_month_revenue:.2f}")

            # Total revenue (all time)
            total_revenue_pipeline = [
                {
                    "$match": {
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            total_revenue_result = await self.orders.aggregate(total_revenue_pipeline).to_list(1)
            total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0.0
            total_revenue_growth_percent = monthly_growth_percent  # Use monthly growth as trend

            logger.info(f"   Total revenue: ${total_revenue:.2f}")

            # ✅ FIX: Weekly revenue breakdown (Mon-Sun) with actual data
            weekly_breakdown_pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": week_start, "$lt": week_end},
                        "payment_status": {"$in": revenue_statuses}
                    }
                },
                {
                    "$project": {
                        "total_amount": 1,
                        "day_of_week": {"$dayOfWeek": "$created_at"}
                    }
                },
                {
                    "$group": {
                        "_id": "$day_of_week",
                        "total": {"$sum": "$total_amount"}
                    }
                }
            ]
            weekly_breakdown_results = await self.orders.aggregate(weekly_breakdown_pipeline).to_list(None)
            
            # Map MongoDB day of week (1=Sunday) to array index (0=Monday)
            breakdown_map = {i: 0.0 for i in range(7)}
            for result in weekly_breakdown_results:
                mongo_day = result["_id"]  # 1=Sunday, 2=Monday, ..., 7=Saturday
                # Convert: Sunday(1) -> 6, Monday(2) -> 0, Tuesday(3) -> 1, etc.
                index = (mongo_day + 5) % 7
                breakdown_map[index] = round(result["total"], 2)

            day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            weekly_revenue_breakdown = []
            for offset in range(7):
                day_date = week_start + timedelta(days=offset)
                weekly_revenue_breakdown.append({
                    "label": day_labels[offset],
                    "date": day_date.strftime("%Y-%m-%d"),
                    "total": breakdown_map.get(offset, 0.0)
                })

            breakdown_log = [f"{d['label']}:${d['total']:.2f}" for d in weekly_revenue_breakdown]
            logger.info("   Weekly breakdown: %s", breakdown_log)

            # Active subscriptions
            active_subs = 0
            subscription_collections = [
                coll for coll in [self.meal_subs, self.weekly_subs_legacy] if coll is not None
            ]
            for coll in subscription_collections:
                try:
                    active_subs += await coll.count_documents({
                        "$or": [
                            {"status": {"$in": ["active", "paused"]}},
                            {"is_active": True},
                        ]
                    })
                except Exception as sub_error:
                    logger.warning(f"Unable to count active subscriptions: {sub_error}")

            # Upcoming catering events
            upcoming_catering = 0
            if self.catering_orders is not None:
                upcoming_catering = await self.catering_orders.count_documents({
                    "event_date": {"$gte": now}
                })

            stats = {
                "total_orders": total_orders,
                "total_orders_growth_percent": total_orders_growth_percent,
                "pending_orders": pending_orders,
                "pending_orders_weekly_change_percent": pending_orders_weekly_change_percent,
                "confirmed_orders": confirmed_orders,
                "preparing_orders": preparing_orders,
                "out_for_delivery_orders": out_for_delivery_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
                "today_revenue": round(today_revenue, 2),
                "today_vs_yesterday_percent": today_vs_yesterday_percent,
                "weekly_revenue": round(weekly_revenue, 2),
                "weekly_growth_percent": weekly_growth_percent,
                "monthly_revenue": round(monthly_revenue, 2),
                "monthly_growth_percent": monthly_growth_percent,
                "total_revenue": round(total_revenue, 2),
                "total_revenue_growth_percent": total_revenue_growth_percent,
                "weekly_revenue_breakdown": weekly_revenue_breakdown,
                "active_subscriptions": active_subs,
                "upcoming_catering_events": upcoming_catering
            }

            logger.info("✅ Dashboard stats calculated successfully")
            return stats

        except Exception as e:
            logger.error(f"❌ Error getting dashboard stats: {e}", exc_info=True)
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict:
        """Return empty stats structure as fallback"""
        return {
            "total_orders": 0,
            "total_orders_growth_percent": 0.0,
            "pending_orders": 0,
            "pending_orders_weekly_change_percent": 0.0,
            "confirmed_orders": 0,
            "preparing_orders": 0,
            "out_for_delivery_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "today_revenue": 0.0,
            "today_vs_yesterday_percent": 0.0,
            "weekly_revenue": 0.0,
            "weekly_growth_percent": 0.0,
            "monthly_revenue": 0.0,
            "monthly_growth_percent": 0.0,
            "total_revenue": 0.0,
            "total_revenue_growth_percent": 0.0,
            "weekly_revenue_breakdown": [
                {"label": "Mon", "date": "", "total": 0.0},
                {"label": "Tue", "date": "", "total": 0.0},
                {"label": "Wed", "date": "", "total": 0.0},
                {"label": "Thu", "date": "", "total": 0.0},
                {"label": "Fri", "date": "", "total": 0.0},
                {"label": "Sat", "date": "", "total": 0.0},
                {"label": "Sun", "date": "", "total": 0.0},
            ],
            "active_subscriptions": 0,
            "upcoming_catering_events": 0
        }
    
    # ... (rest of the methods remain the same - get_all_orders, get_sales_report, etc.)
    
    async def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 50,
        status: str = None,
        order_type: str = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> tuple[List, int]:
        """Get all orders with filters"""
        try:
            if self.orders is None:
                return [], 0
                
            query = {}
            
            if status:
                query["status"] = status
            
            if order_type:
                query["order_type"] = order_type
            
            if date_from or date_to:
                query["created_at"] = {}
                if date_from:
                    query["created_at"]["$gte"] = date_from
                if date_to:
                    query["created_at"]["$lte"] = date_to
            
            # Get total count
            total = await self.orders.count_documents(query)
            
            # Get orders
            cursor = (
                self.orders.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            orders = await cursor.to_list(length=limit)

            serialized_orders: List[Dict] = []
            for order in orders:
                if self.users is not None and order.get("user_id") is not None:
                    user = await self.users.find_one({"_id": order["user_id"]})
                    if user:
                        order["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        order["user_email"] = user.get("email")
                        order["user_phone"] = user.get("phone")

                serialized = {
                    "_id": str(order.get("_id")),
                    "order_number": order.get("order_number"),
                    "user_id": str(order.get("user_id")) if order.get("user_id") is not None else None,
                    "order_type": self._map_order_type(order.get("order_type")),
                    "status": order.get("status"),
                    "payment_status": order.get("payment_status"),
                    "payment_method": order.get("payment_method"),
                    "payment_intent_id": order.get("stripe_payment_intent_id"),
                    "items": order.get("items", []),
                    "subtotal": order.get("subtotal", 0.0),
                    "delivery_fee": order.get("delivery_fee", 0.0),
                    "total_amount": order.get("total_amount", 0.0),
                    "delivery_method": order.get("delivery_method"),
                    "delivery_address": self._normalize_address(order.get("delivery_address")),
                    "delivery_instructions": order.get("delivery_instructions"),
                    "notes": order.get("notes"),
                    "admin_notes": order.get("admin_notes"),
                    "created_at": self._serialize_datetime(order.get("created_at")),
                    "updated_at": self._serialize_datetime(order.get("updated_at")),
                    "delivered_at": self._serialize_datetime(order.get("delivered_at")),
                    "user_name": order.get("user_name"),
                    "user_email": order.get("user_email"),
                    "user_phone": order.get("user_phone"),
                }
                serialized_orders.append(serialized)

            return serialized_orders, total
            
        except Exception as e:
            logger.error(f"Error getting all orders: {e}")
            raise
    
    async def get_sales_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate sales report for date range"""
        try:
            if self.orders is None:
                return {
                    "date_range": {
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d")
                    },
                    "by_order_type": {},
                    "total_orders": 0,
                    "total_revenue": 0.0
                }
                
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$gte": start_date, "$lte": end_date},
                        "payment_status": {"$in": [PaymentStatus.PAID.value, PaymentStatus.PENDING.value]}
                    }
                },
                {
                    "$group": {
                        "_id": "$order_type",
                        "count": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"}
                    }
                }
            ]
            
            results = await self.orders.aggregate(pipeline).to_list(None)
            
            report = {
                "date_range": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                },
                "by_order_type": {},
                "total_orders": 0,
                "total_revenue": 0.0
            }
            
            for result in results:
                order_type = result["_id"]
                report["by_order_type"][order_type] = {
                    "count": result["count"],
                    "revenue": round(result["total_revenue"], 2)
                }
                report["total_orders"] += result["count"]
                report["total_revenue"] += result["total_revenue"]
            
            report["total_revenue"] = round(report["total_revenue"], 2)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating sales report: {e}")
            raise

admin_service = AdminService()
```

---

#### 📄 auth_service.py
**Path:** `app\services\auth_service.py`

```python
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import secrets

from bson import ObjectId

from app.config.database import database
from app.models.user import Address, UserModel
from app.schemas.auth import (
    AddAddressRequest,
    UpdateAddressRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.utils.security import create_access_token, get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class AuthService:
    @property
    def db(self):
        """Get database instance lazily."""
        return database.db

    @property
    def collection(self):
        """Users collection handle."""
        if database.db is not None:
            return database.db.users
        return None

    @property
    def password_reset_tokens(self):
        """Password reset token collection."""
        if self.db is not None:
            return self.db.password_reset_tokens
        return None

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _ensure_datetime(value: Any) -> datetime:
        """Ensure value is a datetime instance."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass
        return datetime.utcnow()

    @staticmethod
    def _stringify_object_id(value: Any) -> Optional[str]:
        """Convert ObjectId or similar value to string safely."""
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return str(value)
        return str(value)

    def _normalize_address_document(
        self, address: Union[dict, Address, None], user_id: str
    ) -> Dict[str, Any]:
        """Ensure an address document contains all required fields for storage."""
        if address is None:
            address_dict: Dict[str, Any] = {}
        elif isinstance(address, Address):
            address_dict = address.model_dump(by_alias=True)
        else:
            address_dict = deepcopy(address)

        address_id = (
            address_dict.get("_id")
            or address_dict.get("id")
            or self._stringify_object_id(ObjectId())
        )
        address_dict["_id"] = self._stringify_object_id(address_id)
        address_dict.pop("id", None)

        address_dict["user_id"] = address_dict.get("user_id") or user_id
        address_dict["label"] = address_dict.get("label") or "Delivery Address"
        address_dict["street"] = address_dict.get("street") or ""
        address_dict["suburb"] = address_dict.get("suburb") or ""
        address_dict["postcode"] = address_dict.get("postcode") or ""
        address_dict["state"] = address_dict.get("state") or "NSW"
        address_dict["country"] = address_dict.get("country") or "Australia"
        address_dict["delivery_instructions"] = address_dict.get(
            "delivery_instructions"
        )
        address_dict["latitude"] = address_dict.get("latitude")
        address_dict["longitude"] = address_dict.get("longitude")
        address_dict["is_default"] = bool(address_dict.get("is_default", False))

        address_dict["created_at"] = self._ensure_datetime(
            address_dict.get("created_at")
        )
        address_dict["updated_at"] = self._ensure_datetime(
            address_dict.get("updated_at")
        )

        return address_dict

    def _address_to_response(self, address: Union[dict, Address], user_id: str) -> Dict[str, Any]:
        """Convert an address document/model to API response payload."""
        normalized = self._normalize_address_document(address, user_id)
        return {
            "_id": normalized["_id"],
            "user_id": normalized["user_id"],
            "label": normalized["label"],
            "street": normalized["street"],
            "suburb": normalized["suburb"],
            "postcode": normalized["postcode"],
            "state": normalized["state"],
            "country": normalized["country"],
            "delivery_instructions": normalized.get("delivery_instructions"),
            "latitude": normalized.get("latitude"),
            "longitude": normalized.get("longitude"),
            "is_default": normalized.get("is_default", False),
            "created_at": normalized["created_at"].isoformat(),
            "updated_at": normalized["updated_at"].isoformat(),
        }

    def _normalize_user_document(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise all addresses inside a raw user document."""
        if not user:
            return user

        user_id = self._stringify_object_id(user.get("_id")) or ""
        addresses = user.get("addresses") or []
        user["addresses"] = [
            self._normalize_address_document(addr, user_id) for addr in addresses
        ]
        return user

    def format_addresses_for_response(
        self, addresses: List[Address], user_id: str
    ) -> List[Dict[str, Any]]:
        """Return addresses formatted for API responses."""
        return [self._address_to_response(addr, user_id) for addr in addresses]

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------
    async def create_access_token(self, data: dict) -> str:
        """Create access token wrapper."""
        return create_access_token(data)

    async def register_user(self, user_data: UserRegisterRequest) -> UserModel:
        """Register a new user."""
        try:
            if self.collection is None:
                logger.error("Database not connected - collection is None")
                raise ValueError("Database not connected")

            logger.info("Attempting to register user: %s", user_data.email)

            if await self.collection.find_one({"email": user_data.email}):
                logger.warning("User with email %s already exists", user_data.email)
                raise ValueError("User with this email already exists")

            if await self.collection.find_one({"phone": user_data.phone}):
                logger.warning("User with phone %s already exists", user_data.phone)
                raise ValueError("User with this phone number already exists")

            now = datetime.utcnow()
            user_dict = {
                "email": user_data.email,
                "phone": user_data.phone,
                "password_hash": get_password_hash(user_data.password),
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "role": "customer",
                "addresses": [],
                "is_active": True,
                "email_verified": False,
                "created_at": now,
                "updated_at": now,
            }

            result = await self.collection.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id

            logger.info(
                "User registered successfully: %s with ID: %s",
                user_data.email,
                result.inserted_id,
            )
            return UserModel(**user_dict)

        except ValueError:
            raise
        except Exception as exc:
            logger.error("Unexpected error registering user: %s", exc, exc_info=True)
            raise ValueError(f"Registration failed: {exc}")

    async def login_user(self, login_data: UserLoginRequest) -> Tuple[UserModel, str]:
        """Login user and return user object with token."""
        try:
            if self.collection is None:
                raise ValueError("Database not connected")

            user = await self.collection.find_one({"email": login_data.email})
            if not user:
                logger.warning("Login failed - user not found: %s", login_data.email)
                raise ValueError("Invalid email or password")

            if not verify_password(login_data.password, user["password_hash"]):
                logger.warning("Login failed - bad password for: %s", login_data.email)
                raise ValueError("Invalid email or password")

            if not user.get("is_active", True):
                logger.warning("Login failed - account disabled for: %s", login_data.email)
                raise ValueError("Account is deactivated")

            if not user.get("email_verified", False):
                logger.warning("Login failed - email not verified for: %s", login_data.email)
                raise ValueError("Please verify your email before logging in.")

            user = self._normalize_user_document(user)
            user_model = UserModel(**user)

            payload = {
                "sub": str(user_model.id),
                "email": user_model.email,
                "role": user_model.role,
                "exp": datetime.utcnow() + timedelta(days=7),
            }
            token = await self.create_access_token(payload)
            return user_model, token

        except ValueError:
            raise
        except Exception as exc:
            logger.error("Login error: %s", exc, exc_info=True)
            raise ValueError("Login failed")

    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        try:
            if self.collection is None:
                logger.warning("Database not connected - returning None")
                return None

            if not ObjectId.is_valid(user_id):
                logger.error("Invalid ObjectId format: %s", user_id)
                return None

            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None

            user = self._normalize_user_document(user)
            return UserModel(**user)

        except Exception as exc:
            logger.error("Error getting user by ID: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Address management
    # ------------------------------------------------------------------
    async def list_addresses(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all addresses for a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return self.format_addresses_for_response(user.addresses, str(user.id))

    async def get_address(self, user_id: str, address_id: str) -> Dict[str, Any]:
        """Return a specific address for a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        for address in user.addresses:
            if self._stringify_object_id(address.id) == address_id:
                return self._address_to_response(address, str(user.id))

        raise ValueError("Address not found")

    async def add_address(
        self, user_id: str, address_data: AddAddressRequest
    ) -> Dict[str, Any]:
        """Add a new address for a user and return it."""
        if self.collection is None:
            raise ValueError("Database not connected")

        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise ValueError("User not found")

        user_doc = self._normalize_user_document(user_doc)
        addresses = user_doc.get("addresses", [])

        now = datetime.utcnow()
        new_address = self._normalize_address_document(
            {
                "_id": str(ObjectId()),
                "user_id": str(user_id),
                "label": address_data.label,
                "street": address_data.street,
                "suburb": address_data.suburb,
                "postcode": address_data.postcode,
                "state": address_data.state,
                "country": address_data.country,
                "delivery_instructions": address_data.delivery_instructions,
                "latitude": address_data.latitude,
                "longitude": address_data.longitude,
                "is_default": address_data.is_default,
                "created_at": now,
                "updated_at": now,
            },
            str(user_id),
        )

        if not addresses:
            new_address["is_default"] = True
        elif new_address["is_default"]:
            for addr in addresses:
                addr["is_default"] = False
        elif not any(addr.get("is_default") for addr in addresses):
            new_address["is_default"] = True

        addresses.append(new_address)

        if not any(addr.get("is_default") for addr in addresses):
            if addresses:
                addresses[0]["is_default"] = True
                addresses[0]["updated_at"] = now

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"addresses": addresses, "updated_at": now}},
        )
        if result.modified_count == 0:
            raise ValueError("Failed to add address")

        logger.info("Address added successfully for user: %s", user_id)
        return self._address_to_response(new_address, str(user_id))

    async def update_address(
        self, user_id: str, address_id: str, update_data: UpdateAddressRequest
    ) -> Dict[str, Any]:
        """Update an address and return the updated record."""
        if self.collection is None:
            raise ValueError("Database not connected")

        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

        updates = update_data.dict(exclude_unset=True)
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise ValueError("User not found")

        user_doc = self._normalize_user_document(user_doc)
        addresses = user_doc.get("addresses", [])

        target = None
        for addr in addresses:
            if self._stringify_object_id(addr.get("_id")) == address_id:
                target = addr
                break

        if not target:
            raise ValueError("Address not found")

        now = datetime.utcnow()

        if "is_default" in updates and updates["is_default"]:
            for addr in addresses:
                addr["is_default"] = False
            target["is_default"] = True
        elif "is_default" in updates and not updates["is_default"]:
            target["is_default"] = False

        for field in [
            "label",
            "street",
            "suburb",
            "postcode",
            "state",
            "country",
            "delivery_instructions",
            "latitude",
            "longitude",
        ]:
            if field in updates and updates[field] is not None:
                target[field] = updates[field]

        target["updated_at"] = now

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"addresses": addresses, "updated_at": now}},
        )
        if result.modified_count == 0:
            raise ValueError("Failed to update address")

        logger.info("Address %s updated for user %s", address_id, user_id)
        return self._address_to_response(target, str(user_id))

    async def delete_address(self, user_id: str, address_id: str) -> None:
        """Delete an address."""
        if self.collection is None:
            raise ValueError("Database not connected")

        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise ValueError("User not found")

        user_doc = self._normalize_user_document(user_doc)
        addresses = user_doc.get("addresses", [])

        updated_addresses = []
        removed = None
        for addr in addresses:
            if self._stringify_object_id(addr.get("_id")) == address_id:
                removed = addr
                continue
            updated_addresses.append(addr)

        if removed is None:
            raise ValueError("Address not found")

        if removed.get("is_default") and updated_addresses:
            updated_addresses[0]["is_default"] = True
            updated_addresses[0]["updated_at"] = datetime.utcnow()

        now = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"addresses": updated_addresses, "updated_at": now}},
        )

        logger.info("Address %s deleted for user %s", address_id, user_id)

    async def set_default_address(self, user_id: str, address_id: str) -> Dict[str, Any]:
        """Set an address as default."""
        return await self.update_address(
            user_id, address_id, UpdateAddressRequest(is_default=True)
        )

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    async def update_profile(self, user_id: str, update_data: dict) -> UserModel:
        """Update user profile."""
        if self.collection is None:
            raise ValueError("Database not connected")

        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            logger.warning("No changes made to user profile: %s", user_id)

        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("Failed to retrieve updated user")

        logger.info("Profile updated for user: %s", user_id)
        return user

    # ------------------------------------------------------------------
    # Password reset
    # ------------------------------------------------------------------
    async def create_password_reset_request(self, email: str) -> Optional[Tuple[str, UserModel]]:
        """Create a password reset token and return it with the user."""
        if self.collection is None or self.password_reset_tokens is None:
            raise ValueError("Database not connected")

        user_doc = await self.collection.find_one({"email": email})
        if not user_doc:
            raise ValueError("No account found for this email address")

        normalized = self._normalize_user_document(user_doc)
        user = UserModel(**normalized)

        token = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        await self.password_reset_tokens.update_many(
            {"email": email, "used": False},
            {"$set": {"used": True, "used_at": datetime.utcnow()}},
        )

        await self.password_reset_tokens.insert_one(
            {
                "email": email,
                "token": token,
                "used": False,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
            }
        )

        return token, user

    async def reset_password_with_token(self, email: str, token: str, new_password: str) -> bool:
        """Validate reset token and update password."""
        if self.collection is None or self.password_reset_tokens is None:
            raise ValueError("Database not connected")

        token_doc = await self.password_reset_tokens.find_one(
            {"email": email, "token": token, "used": False}
        )
        if not token_doc:
            logger.warning("Invalid password reset token for %s", email)
            return False

        if token_doc.get("expires_at") and token_doc["expires_at"] < datetime.utcnow():
            logger.warning("Expired password reset token for %s", email)
            return False

        password_hash = get_password_hash(new_password)
        result = await self.collection.update_one(
            {"email": email},
            {"$set": {"password_hash": password_hash, "updated_at": datetime.utcnow()}},
        )

        if result.modified_count == 0:
            logger.error("Failed to update password for %s", email)
            return False

        await self.password_reset_tokens.update_one(
            {"_id": token_doc["_id"]},
            {"$set": {"used": True, "used_at": datetime.utcnow()}},
        )

        logger.info("Password reset successful for %s", email)
        return True

    # ------------------------------------------------------------------
    # Email Verification
    # ------------------------------------------------------------------
    async def generate_verification_code(self, email: str) -> str:
        """Generate and store a verification code for email verification."""
        import random
        import string
        
        if self.db is None:
            raise ValueError("Database not connected")
        
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Expires in 15 minutes
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Invalidate any existing codes for this email
        await self.db.verification_codes.update_many(
            {"email": email, "used": False},
            {"$set": {"used": True}}
        )
        
        # Store new verification code
        verification_doc = {
            "email": email,
            "code": code,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.utcnow()
        }
        
        await self.db.verification_codes.insert_one(verification_doc)
        
        logger.info("Verification code generated for email: %s", email)
        return code
    
    async def verify_email_code(self, email: str, code: str) -> bool:
        """Verify the email verification code."""
        if self.db is None:
            raise ValueError("Database not connected")
        
        # Find the verification code
        verification = await self.db.verification_codes.find_one({
            "email": email,
            "code": code,
            "used": False
        })
        
        if not verification:
            logger.warning("Invalid verification code for email: %s", email)
            return False
        
        # Check if code is expired
        if verification["expires_at"] < datetime.utcnow():
            logger.warning("Expired verification code for email: %s", email)
            return False
        
        # Mark code as used
        await self.db.verification_codes.update_one(
            {"_id": verification["_id"]},
            {"$set": {"used": True}}
        )
        
        # Update user as verified
        await self.collection.update_one(
            {"email": email},
            {"$set": {"email_verified": True, "updated_at": datetime.utcnow()}}
        )
        
        logger.info("Email verified successfully for: %s", email)
        return True
    
    async def resend_verification_code(self, email: str) -> str:
        """Resend verification code for an email."""
        if self.collection is None:
            raise ValueError("Database not connected")
        
        # Check if user exists
        user = await self.collection.find_one({"email": email})
        if not user:
            raise ValueError("User not found")
        
        # Check if already verified
        if user.get("email_verified", False):
            raise ValueError("Email already verified")
        
        # Generate new code
        code = await self.generate_verification_code(email)
        return code


# Singleton service instance
auth_service = AuthService()
```

---

#### 📄 cart_service.py
**Path:** `app\services\cart_service.py`

```python
from typing import Dict, List
from bson import ObjectId
from app.config.database import get_database
from app.services.menu_service import menu_service
import logging

logger = logging.getLogger(__name__)


class CartService:
    def __init__(self):
        self._db = None
        self._carts = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def carts(self):
        if self._carts is None and self.db is not None:
            self._carts = self.db.carts
        return self._carts

    async def get_cart(self, user_id: str) -> Dict:
        """Fetch or create a user's cart."""
        if self.carts is None:
            raise ValueError("Carts collection not available")

        cart = await self.carts.find_one({"user_id": ObjectId(user_id)})
        if not cart:
            cart = {
                "user_id": ObjectId(user_id),
                "items": [],
            }
            result = await self.carts.insert_one(cart)
            cart["_id"] = result.inserted_id
        return cart

    async def add_to_cart(self, user_id: str, item_id: str, quantity: int) -> Dict:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        cart = await self.get_cart(user_id)

        # Ensure menu item exists
        menu_item = await menu_service.get_menu_item_by_id(item_id)
        if not menu_item:
            raise ValueError("Menu item not found")

        existing_item = next(
            (item for item in cart["items"] if item["item_id"] == item_id),
            None,
        )

        if existing_item:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id), "items.item_id": item_id},
                {"$inc": {"items.$.quantity": quantity}},
            )
        else:
            cart_item = {
                "item_id": item_id,
                "item_name": menu_item.name,
                "category": menu_item.category,
                "price": menu_item.price,
                "quantity": quantity,
            }
            await self.carts.update_one(
                {"user_id": ObjectId(user_id)},
                {"$push": {"items": cart_item}},
            )

        return await self.get_cart_summary(user_id)

    async def update_cart_item(self, user_id: str, item_id: str, quantity: int) -> Dict:
        if self.carts is None:
            raise ValueError("Carts collection not available")

        if quantity <= 0:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id)},
                {"$pull": {"items": {"item_id": item_id}}},
            )
        else:
            await self.carts.update_one(
                {"user_id": ObjectId(user_id), "items.item_id": item_id},
                {"$set": {"items.$.quantity": quantity}},
            )

        return await self.get_cart_summary(user_id)

    async def remove_from_cart(self, user_id: str, item_id: str) -> Dict:
        if self.carts is None:
            raise ValueError("Carts collection not available")

        await self.carts.update_one(
            {"user_id": ObjectId(user_id)},
            {"$pull": {"items": {"item_id": item_id}}},
        )
        return await self.get_cart_summary(user_id)

    async def get_cart_summary(self, user_id: str) -> Dict:
        cart = await self.get_cart(user_id)
        items: List[Dict] = []
        subtotal = 0.0

        for item in cart.get("items", []):
            item_subtotal = item["price"] * item["quantity"]
            items.append(
                {
                    "item_id": item["item_id"],
                    "item_name": item["item_name"],
                    "category": item.get("category", ""),
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "subtotal": item_subtotal,
                }
            )
            subtotal += item_subtotal

        return {
            "items": items,
            "subtotal": subtotal,
            "items_count": len(items),
            "delivery_fee": 0.0,
            "total": subtotal,
        }

    async def clear_cart(self, user_id: str) -> bool:
        if self.carts is None:
            logger.warning("Carts collection not available")
            return False

        await self.carts.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {"items": []}},
        )
        logger.info(f"Cart cleared for user {user_id}")
        return True


cart_service = CartService()
```

---

#### 📄 delivery_service.py
**Path:** `app\services\delivery_service.py`

```python
from typing import Optional, Tuple, List, Dict
from copy import deepcopy
from datetime import datetime
import googlemaps
from app.config.settings import settings
from app.config.database import get_database
from app.utils.helpers import calculate_distance
from app.utils.constants import (
    DAILY_DELIVERY_FEE,
    DAILY_DELIVERY_RADIUS,
    DEFAULT_EXPRESS_FEE_PER_DAY,
)
from app.utils.default_delivery_zones import DEFAULT_MEAL_DELIVERY_ZONES
import logging

logger = logging.getLogger(__name__)

class DeliveryService:
    def __init__(self):
        self.gmaps = None
        self._db = None
        self._zones = None
        self._seeded_defaults = False
        self.business_lat = settings.BUSINESS_LATITUDE
        self.business_lng = settings.BUSINESS_LONGITUDE
        
        # Initialize Google Maps client only if API key is available and valid
        if settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_MAPS_API_KEY != "your-google-maps-api-key":
            try:
                self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps client: {e}")
                logger.warning("Delivery service will work with limited functionality")
        else:
            logger.warning("Google Maps API key not configured. Using fallback delivery calculation.")
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def zones(self):
        """Get delivery_zones collection lazily"""
        if self._zones is None and self.db is not None:  # ✅ Fixed
            self._zones = self.db.delivery_zones
        return self._zones

    async def ensure_default_zones(self) -> None:
        """Seed default meal subscription delivery zones when collection is empty."""
        if self._seeded_defaults:
            return

        if self.zones is None:
            return

        try:
            count = await self.zones.count_documents({})
            if count > 0:
                self._seeded_defaults = True
                return

            now = datetime.utcnow()
            documents: List[Dict[str, object]] = []
            for zone in DEFAULT_MEAL_DELIVERY_ZONES:
                payload = deepcopy(zone)
                payload.setdefault("state", "NSW")
                payload.setdefault("order_types", ["meal_subscription"])
                payload.setdefault("is_active", True)
                payload["created_at"] = now
                payload["updated_at"] = now
                documents.append(payload)

            if documents:
                await self.zones.insert_many(documents)
                logger.info("Seeded %d default delivery zones for meal subscriptions", len(documents))

            self._seeded_defaults = True
        except Exception as exc:
            logger.error(f"Failed to seed default delivery zones: {exc}")
    
    @staticmethod
    def _extract_postcode(address: str) -> Optional[str]:
        """Extract Australian postcode (4 digits) from a string."""
        if not address:
            return None
        import re
        match = re.search(r'\b(\d{4})\b', address)
        return match.group(1) if match else None

    async def _find_zone_by_postcode(self, postcode: Optional[str]) -> Optional[dict]:
        """Lookup delivery zone by postcode if available."""
        if not postcode:
            return None

        if self.zones is None:
            for zone in DEFAULT_MEAL_DELIVERY_ZONES:
                if zone["postcode"] == postcode and zone.get("is_active", True):
                    return deepcopy(zone)
            return None

        await self.ensure_default_zones()
        cursor = self.zones.find({"postcode": postcode, "is_active": True}).sort("base_delivery_fee", 1)
        matches = await cursor.to_list(length=1)
        return matches[0] if matches else None
    
    async def check_daily_delivery(self, address: str) -> Tuple[bool, Optional[float], Optional[dict], Optional[str]]:
        """
        Check if address is within daily delivery range.

        Returns:
            (is_available, distance_km, geocoded_address, failure_reason)
        """
        try:
            failure_reason = None

            if self.gmaps:
                # Use Google Maps for accurate geocoding
                geocode_result = self.gmaps.geocode(address)

                if not geocode_result:
                    failure_reason = (
                        "We could not verify this address. Please double-check the details "
                        "or select another address within our delivery area."
                    )
                    return False, None, None, failure_reason

                location = geocode_result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']

                # Calculate distance
                distance = calculate_distance(
                    self.business_lat, self.business_lng,
                    lat, lng
                )

                is_available = distance <= DAILY_DELIVERY_RADIUS
                if not is_available:
                    failure_reason = (
                        f"This address is {distance:.1f}km away. "
                        f"Daily delivery is limited to {DAILY_DELIVERY_RADIUS:.0f}km from Guildford."
                    )

                geocoded_data = {
                    "formatted_address": geocode_result[0]['formatted_address'],
                    "latitude": lat,
                    "longitude": lng
                }

                logger.info(f"Daily delivery check: {address} - {distance}km - Available: {is_available}")
                return is_available, distance, geocoded_data, failure_reason

            # Fallback: Simple postcode-based check
            logger.info("Using fallback delivery check (postcode-based)")

            postcode = self._extract_postcode(address)
            if postcode:
                zone = await self.check_postcode_coverage(postcode)

                if zone and zone.get("is_covered"):
                    distance = zone.get("distance_km", 5.0)
                    is_available = distance <= DAILY_DELIVERY_RADIUS
                    if not is_available:
                        failure_reason = (
                            f"Daily delivery is limited to {DAILY_DELIVERY_RADIUS:.0f}km from Guildford. "
                            f"This address is approximately {distance:.1f}km away."
                        )

                    geocoded_data = {
                        "formatted_address": address,
                        "latitude": self.business_lat,
                        "longitude": self.business_lng
                    }

                    return is_available, distance, geocoded_data, failure_reason

            failure_reason = (
                f"We currently deliver daily orders within {DAILY_DELIVERY_RADIUS:.0f}km of Guildford. "
                "Please choose an address inside this range."
            )
            return False, None, {
                "formatted_address": address,
                "latitude": self.business_lat,
                "longitude": self.business_lng
            }, failure_reason

        except Exception as e:
            logger.error(f"Error checking daily delivery: {e}")
            return False, None, None, (
                "Unable to verify address for daily delivery right now. "
                "Please try again or contact support."
            )
    
    async def calculate_weekly_delivery_fee(
        self, 
        address: str, 
        order_value: float, 
        delivery_days: int,
        is_express: bool = False
    ) -> Tuple[float, float, dict]:
        """
        Calculate weekly delivery fee
        
        Returns:
            (delivery_fee, distance_km, geocoded_address)
        """
        try:
            formatted_address = address
            distance = None
            lat = self.business_lat
            lng = self.business_lng

            if self.gmaps:
                geocode_result = self.gmaps.geocode(address)

                if not geocode_result:
                    raise ValueError("Invalid address")

                formatted_address = geocode_result[0]['formatted_address']
                location = geocode_result[0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                distance = calculate_distance(
                    self.business_lat, self.business_lng, lat, lng
                )

            postcode = self._extract_postcode(formatted_address)
            zone = await self._find_zone_by_postcode(postcode)

            if zone and zone.get("distance_from_business") is not None:
                distance = zone["distance_from_business"]

            if distance is None:
                distance = calculate_distance(
                    self.business_lat, self.business_lng, lat, lng
                )

            geocoded_data = {
                "formatted_address": formatted_address,
                "latitude": lat,
                "longitude": lng
            }

            base_fee_per_day = 10.0
            express_fee_per_day = DEFAULT_EXPRESS_FEE_PER_DAY if is_express else 0.0

            if zone:
                base_fee_per_day = zone.get("base_delivery_fee", base_fee_per_day)
                if is_express:
                    express_fee_per_day = zone.get("express_delivery_fee", express_fee_per_day)

                max_days = zone.get("max_delivery_days")
                if max_days and delivery_days > max_days:
                    logger.warning(
                        "Requested delivery days (%s) exceed zone max (%s) for postcode %s",
                        delivery_days,
                        max_days,
                        postcode,
                    )

            total_delivery_fee = (base_fee_per_day * delivery_days) + (express_fee_per_day * delivery_days)

            logger.info(
                "Meal subscription delivery fee: base=%s express=%s days=%s total=%s postcode=%s",
                base_fee_per_day,
                express_fee_per_day if is_express else 0.0,
                delivery_days,
                total_delivery_fee,
                postcode,
            )
            return total_delivery_fee, distance, geocoded_data
            
        except Exception as e:
            logger.error(f"Error calculating weekly delivery fee: {e}")
            # Return default fee to not break the service
            base_fee = 10.0 * delivery_days
            if is_express:
                base_fee += DEFAULT_EXPRESS_FEE_PER_DAY * delivery_days
            
            return base_fee, 10.0, {
                "formatted_address": address,
                "latitude": self.business_lat,
                "longitude": self.business_lng
            }
    
    async def check_postcode_coverage(self, postcode: str) -> Optional[dict]:
        """Check if postcode is covered"""
        try:
            if self.zones is None:  # ✅ Fixed
                matches = [
                    deepcopy(zone)
                    for zone in DEFAULT_MEAL_DELIVERY_ZONES
                    if zone["postcode"] == postcode and zone.get("is_active", True)
                ]
                if matches:
                    primary = matches[0]
                    response = {
                        "suburbs": primary.get("suburbs", []),
                        "postcode": primary["postcode"],
                        "distance_km": primary.get("distance_from_business"),
                        "base_delivery_fee": primary.get("base_delivery_fee"),
                        "notes": primary.get("notes"),
                        "is_covered": True,
                    }
                    if len(matches) > 1:
                        response["alternatives"] = [
                            {
                                "zone_label": zone.get("zone_label"),
                                "suburbs": zone.get("suburbs", []),
                                "base_delivery_fee": zone.get("base_delivery_fee"),
                                "notes": zone.get("notes"),
                            }
                            for zone in matches[1:]
                        ]
                    return response
                return {"is_covered": False}

            await self.ensure_default_zones()
            cursor = self.zones.find({"postcode": postcode, "is_active": True}).sort("base_delivery_fee", 1)
            zones = await cursor.to_list(length=None)

            if zones:
                primary = zones[0]
                response = {
                    "suburbs": primary.get("suburbs", []),
                    "postcode": primary["postcode"],
                    "distance_km": primary.get("distance_from_business"),
                    "base_delivery_fee": primary.get("base_delivery_fee"),
                    "notes": primary.get("notes"),
                    "is_covered": True,
                }
                if len(zones) > 1:
                    response["alternatives"] = [
                        {
                            "zone_label": zone.get("zone_label"),
                            "suburbs": zone.get("suburbs", []),
                            "base_delivery_fee": zone.get("base_delivery_fee"),
                            "notes": zone.get("notes"),
                        }
                        for zone in zones[1:]
                    ]
                return response

            return {"is_covered": False}
            
        except Exception as e:
            logger.error(f"Error checking postcode: {e}")
            return {"is_covered": True, "base_delivery_fee": 10.0}  # Default to covered to not break service
    
    async def get_available_suburbs(self) -> list:
        """Get list of all available suburbs"""
        try:
            if self.zones is None:  # ✅ Fixed
                return [
                    {
                        "postcode": zone.get("postcode"),
                        "zone_label": zone.get("zone_label"),
                        "suburbs": zone.get("suburbs", []),
                        "distance_km": zone.get("distance_from_business"),
                        "base_delivery_fee": zone.get("base_delivery_fee"),
                        "notes": zone.get("notes"),
                        "order_types": zone.get("order_types", []),
                    }
                    for zone in DEFAULT_MEAL_DELIVERY_ZONES
                    if zone.get("is_active", True)
                ]
            
            await self.ensure_default_zones()
            cursor = self.zones.find({"is_active": True}).sort("postcode", 1)
            zones = await cursor.to_list(length=None)
            
            return [
                {
                    "postcode": zone.get("postcode"),
                    "zone_label": zone.get("zone_label"),
                    "suburbs": zone.get("suburbs") or ([zone["suburb"]] if zone.get("suburb") else []),
                    "distance_km": zone.get("distance_from_business"),
                    "base_delivery_fee": zone.get("base_delivery_fee"),
                    "notes": zone.get("notes"),
                    "order_types": zone.get("order_types", []),
                }
                for zone in zones
            ]
            
        except Exception as e:
            logger.error(f"Error getting suburbs: {e}")
            return []

delivery_service = DeliveryService()
```

---

#### 📄 email_service.py
**Path:** `app\services\email_service.py`

```python
import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Iterable, Optional, List
import html
from datetime import datetime

from fastapi.concurrency import run_in_threadpool

from app.config.settings import settings
from app.models.order import OrderModel, OrderItem

logger = logging.getLogger(__name__)


class EmailNotConfiguredError(RuntimeError):
    """Raised when SMTP settings are missing."""


def _build_email_message(
    subject: str,
    body_text: str,
    body_html: Optional[str],
    recipients: Iterable[str],
    reply_to: Optional[str] = None,
) -> EmailMessage:
    message = EmailMessage()
    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME

    if not from_email:
        raise EmailNotConfiguredError("SMTP sender email is not configured.")

    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
    message["To"] = ", ".join(recipients)

    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(body_text)

    if body_html:
        message.add_alternative(body_html, subtype="html")

    return message


def _send_email(message: EmailMessage) -> None:
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD

    if not (host and port and username and password):
        raise EmailNotConfiguredError("SMTP credentials are not fully configured.")

    context = ssl.create_default_context()

    with smtplib.SMTP(host, port, timeout=30) as server:
        if settings.SMTP_USE_TLS:
            server.starttls(context=context)

        server.login(username, password)
        server.send_message(message)

    logger.info("Email successfully sent to %s", message["To"])


async def send_email_async(
    *,
    subject: str,
    body_text: str,
    recipients: Iterable[str],
    body_html: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> None:
    """
    Asynchronously send an email using the configured SMTP server.
    """
    message = _build_email_message(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=recipients,
        reply_to=reply_to,
    )

    await run_in_threadpool(_send_email, message)


def _format_currency(amount: Optional[float]) -> str:
    try:
        return f"${float(amount):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def _format_datetime(value: Optional[datetime]) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value) if value else "N/A"


def _extract_order_items(order: OrderModel) -> List[OrderItem]:
    items: List[OrderItem] = []
    for entry in order.items:
        if isinstance(entry, OrderItem):
            items.append(entry)
        else:
            items.append(OrderItem(**entry))
    return items


def _format_address_block(order: OrderModel) -> str:
    if order.delivery_method == "pickup" or not order.delivery_address:
        return "Pickup order - we'll notify you when it's ready."

    addr = order.delivery_address
    if hasattr(addr, "dict"):
        addr = addr.dict()

    lines = [addr.get("street"), f"{addr.get('suburb', '')} {addr.get('postcode', '')}".strip()]
    return "<br/>".join(filter(None, lines)) if any(lines) else "Delivery address on file."


async def send_order_confirmation_email(
    *,
    order: OrderModel,
    customer_email: Optional[str],
    customer_name: Optional[str] = "",
    restaurant_email: Optional[str] = None,
) -> None:
    """Send an order confirmation email to the customer and restaurant."""
    recipient_candidates = [customer_email, restaurant_email]
    recipients: List[str] = []
    seen = set()
    for email in recipient_candidates:
        if email:
            normalized = email.strip().lower()
            if normalized and normalized not in seen:
                recipients.append(email.strip())
                seen.add(normalized)

    if not recipients:
        logger.info("Skipping order confirmation email; no recipients provided.")
        return

    friendly_name = customer_name or "there"
    order_date = _format_datetime(order.created_at)
    delivery_summary = _format_address_block(order)
    payment_method = (order.payment_method or "cash").title()
    raw_order_type = str(order.order_type or "order")
    raw_payment_status = str(order.payment_status or "pending")
    order_type_label = raw_order_type.split(".")[-1].replace("_", " ").title()
    payment_status_label = raw_payment_status.split(".")[-1].replace("_", " ").title()

    items = _extract_order_items(order)
    item_lines_text = [
        f"- {item.item_name} x{item.quantity} @ {_format_currency(item.price)} = {_format_currency(item.subtotal)}"
        for item in items
    ] or ["(No items recorded)"]

    text_lines = [
        f"Hi {friendly_name},",
        "",
        "Thank you for ordering from Bakar's Food & Catering!",
        f"Order Number: {order.order_number}",
        f"Order Date: {order_date}",
        f"Order Type: {order_type_label}",
        "",
        "Items:",
        *item_lines_text,
        "",
        "Summary:",
        f"Subtotal: {_format_currency(order.subtotal)}",
        f"Delivery Fee: {_format_currency(order.delivery_fee)}",
        f"Total: {_format_currency(order.total_amount)}",
        f"Payment Method: {payment_method}",
        f"Payment Status: {payment_status_label}",
        "",
        "Delivery / Pickup:",
        delivery_summary.replace("<br/>", "\n"),
    ]

    if order.delivery_instructions:
        text_lines.extend(
            [
                "",
                "Delivery Instructions:",
                order.delivery_instructions,
            ]
        )

    if restaurant_email:
        text_lines.extend(
            [
                "",
                f"A copy of this email was also sent to {restaurant_email} so our team can prepare right away.",
            ]
        )

    text_lines.extend(
        [
            "",
            "We'll email you again as your order progresses. If you have any questions, simply reply to this email.",
            "",
            "Warm regards,",
            "Bakar's Food & Catering",
        ]
    )

    item_rows_html = "".join(
        f"""
        <tr>
            <td>{html.escape(item.item_name)}</td>
            <td style="text-align:center;">{item.quantity}</td>
            <td style="text-align:right;">{_format_currency(item.price)}</td>
            <td style="text-align:right;">{_format_currency(item.subtotal)}</td>
        </tr>
        """
        for item in items
    )

    restaurant_copy_note = ""
    if restaurant_email:
        restaurant_copy_note = (
            f"This email was sent to you and our restaurant team "
            f"({html.escape(restaurant_email)}). "
        )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            body {{ font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6; }}
            .container {{ max-width: 640px; margin: 0 auto; padding: 24px; background: #ffffff; }}
            .header {{ border-bottom: 2px solid #ff6b35; margin-bottom: 24px; }}
            .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            .summary-table th, .summary-table td {{ border-bottom: 1px solid #f1f5f9; padding: 8px; }}
            .summary-table th {{ text-align: left; background: #f8fafc; }}
            .totals {{ margin-top: 16px; }}
            .totals div {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
            .footer {{ margin-top: 32px; font-size: 13px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Order Confirmation #{order.order_number}</h2>
                <p>{order_date}</p>
            </div>
            <p>Hi {html.escape(friendly_name)},</p>
            <p>Thank you for ordering from <strong>Bakar's Food &amp; Catering</strong>.</p>
            <p><strong>Order Type:</strong> {html.escape(order_type_label)}<br/>
               <strong>Payment Method:</strong> {html.escape(payment_method)}<br/>
               <strong>Payment Status:</strong> {html.escape(payment_status_label)}</p>

            <table class="summary-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows_html or '<tr><td colspan="4">No items</td></tr>'}
                </tbody>
            </table>

            <div class="totals">
                <div><span>Subtotal</span><strong>{_format_currency(order.subtotal)}</strong></div>
                <div><span>Delivery Fee</span><strong>{_format_currency(order.delivery_fee)}</strong></div>
                <div><span>Total</span><strong>{_format_currency(order.total_amount)}</strong></div>
            </div>

            <div style="margin-top:24px;">
                <h3>Delivery / Pickup</h3>
                <p>{delivery_summary}</p>
            </div>
            {"<div style='margin-top:24px;'><h3>Delivery Instructions</h3><p>" + html.escape(order.delivery_instructions) + "</p></div>" if order.delivery_instructions else ""}

            <p class="footer">
                {restaurant_copy_note or ''}
                If you have questions, just reply to this email.
            </p>
        </div>
    </body>
    </html>
    """

    await send_email_async(
        subject=f"Order Confirmation #{order.order_number}",
        body_text="\n".join(text_lines),
        body_html=body_html,
        recipients=recipients,
    )


async def send_contact_email(
    *,
    name: str,
    email: str,
    phone: str,
    message: str,
) -> None:
    """
    Send a contact form email to the configured recipient.
    """
    recipient = settings.CONTACT_RECIPIENT_EMAIL or settings.SMTP_FROM_EMAIL

    if not recipient:
        raise EmailNotConfiguredError("Contact recipient email is not configured.")

    subject = f"New contact enquiry from {name}"
    body_text = (
        f"You received a new contact enquiry on Bakar's website.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n\n"
        f"Message:\n{message}\n"
    )
    body_html = f"""
    <p>You received a new contact enquiry on <strong>Bakar's Food &amp; Catering</strong>.</p>
    <ul>
      <li><strong>Name:</strong> {name}</li>
      <li><strong>Email:</strong> {email}</li>
      <li><strong>Phone:</strong> {phone}</li>
    </ul>
    <p><strong>Message:</strong></p>
    <p>{message.replace(chr(10), '<br/>')}</p>
    """

    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[recipient],
        reply_to=email,
    )


async def send_verification_email(
    *,
    email: str,
    name: str,
    code: str,
) -> None:
    """
    Send email verification code to the user.
    """
    subject = "Verify Your Email - Bakar's Food & Catering"
    
    body_text = (
        f"Hi {name},\n\n"
        f"Thank you for registering with Bakar's Food & Catering!\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"If you didn't create an account, please ignore this email.\n\n"
        f"Best regards,\n"
        f"Bakar's Food & Catering Team"
    )
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #ff6b35; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .code-box {{ background-color: #fff; border: 2px dashed #ff6b35; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px; }}
            .code {{ font-size: 32px; font-weight: bold; color: #ff6b35; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Bakar's!</h1>
            </div>
            <div class="content">
                <p>Hi {name},</p>
                <p>Thank you for registering with <strong>Bakar's Food & Catering</strong>!</p>
                <p>Please use the following code to verify your email address:</p>
                <div class="code-box">
                    <div class="code">{code}</div>
                </div>
                <p><strong>This code will expire in 15 minutes.</strong></p>
                <p>If you didn't create an account, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br/>Bakar's Food & Catering Team</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[email],
    )


async def send_password_reset_email(
    *,
    email: str,
    name: str,
    reset_link: str,
) -> None:
    """Send password reset link email."""
    subject = "Reset Your Password - Bakar's Food & Catering"
    body_text = (
        f"Hi {name},\n\n"
        f"We received a request to reset the password for your Bakar's Food & Catering account.\n"
        f"You can reset your password by visiting the link below:\n\n"
        f"{reset_link}\n\n"
        "This link will expire in 60 minutes. If you did not request a password reset, you can safely ignore this email.\n\n"
        "Best regards,\n"
        "Bakar's Food & Catering Team"
    )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 14px 28px;
                background-color: #ff6b35;
                color: #fff !important;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .note {{ font-size: 12px; color: #777; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hi {name},</p>
            <p>We received a request to reset the password for your <strong>Bakar's Food &amp; Catering</strong> account.</p>
            <p>Click the button below to set a new password.</p>
            <p style="text-align:center;">
                <a class="button" href="{reset_link}" target="_blank">Reset Password</a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p><a href="{reset_link}" target="_blank">{reset_link}</a></p>
            <p class="note">This link will expire in 60 minutes. If you did not request a password reset, please ignore this email.</p>
            <p>Best regards,<br/>Bakar's Food &amp; Catering Team</p>
        </div>
    </body>
    </html>
    """

    await send_email_async(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        recipients=[email],
    )
```

---

#### 📄 menu_service.py
**Path:** `app\services\menu_service.py`

```python
from typing import List, Optional, Tuple, Dict, Any, Set
from bson import ObjectId
from datetime import datetime
from app.config.database import database
from app.models.menu import MenuItemModel, CategoryModel, WeeklyMenuScheduleModel
import logging

logger = logging.getLogger(__name__)

ADD_ONS_CATEGORY_ALIASES = {
    "add ons",
    "addons",
    "add on",
}
ADD_ONS_CATEGORY_REGEX = r"^add[\s\-_]*ons?$"

class MenuService:
    """Service layer for menu operations"""

    @staticmethod
    def _normalize_category_value(value: Optional[str]) -> str:
        if not value:
            return ""
        normalized = value.lower()
        for char in ("_", "-", "'"):
            normalized = normalized.replace(char, " ")
        normalized = " ".join(normalized.split())
        return normalized

    def _is_addons_category(self, value: Optional[str]) -> bool:
        normalized = self._normalize_category_value(value)
        return normalized in ADD_ONS_CATEGORY_ALIASES

    def _addons_regex_condition(self) -> Dict[str, Any]:
        return {"$regex": ADD_ONS_CATEGORY_REGEX, "$options": "i"}

    @staticmethod
    def _build_variant_group_key(item: Dict[str, Any]) -> Tuple[str, str, float, str]:
        """Create a grouping key to identify legacy duplicate program variants."""
        name = str(item.get("name") or "").strip().lower()
        category = str(item.get("category") or "").strip().lower()
        description = str(item.get("description") or "").strip().lower()
        price_raw = item.get("price", 0)
        try:
            price = float(price_raw or 0)
        except (TypeError, ValueError):
            price = 0.0
        return (name, category, price, description)

    @staticmethod
    def _deduplicate_ordered(values: List[Any]) -> List[Any]:
        """Remove duplicates from a list while preserving order."""
        seen: Set[str] = set()
        deduped: List[Any] = []
        for value in values:
            key = str(value)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)
        return deduped

    async def _replace_ids_in_weekly_schedule(self, replacements: Dict[str, str]) -> int:
        """Update weekly menu schedules to point to the consolidated menu item IDs."""
        if self.weekly_schedule is None or not replacements:
            return 0

        object_id_map: Dict[ObjectId, ObjectId] = {}
        for old_id, new_id in replacements.items():
            if ObjectId.is_valid(old_id) and ObjectId.is_valid(new_id):
                object_id_map[ObjectId(old_id)] = ObjectId(new_id)

        if not object_id_map:
            return 0

        cursor = self.weekly_schedule.find({"menu_items": {"$in": list(object_id_map.keys())}})
        schedules = await cursor.to_list(length=None)
        updated = 0

        for schedule in schedules:
            original_items = schedule.get("menu_items", []) or []
            new_items: List[ObjectId] = []
            changed = False

            for item_id in original_items:
                replacement = object_id_map.get(item_id)
                if replacement is not None:
                    new_items.append(replacement)
                    changed = True
                else:
                    new_items.append(item_id)

            if changed:
                deduped_items = self._deduplicate_ordered(new_items)
                await self.weekly_schedule.update_one(
                    {"_id": schedule["_id"]},
                    {"$set": {"menu_items": deduped_items, "updated_at": datetime.utcnow()}},
                )
                updated += 1

        return updated

    async def _replace_ids_in_meal_plans(self, replacements: Dict[str, str]) -> int:
        """Update meal plan templates to use the consolidated menu item IDs."""
        if self.meal_plans is None or not replacements:
            return 0

        cursor = self.meal_plans.find({"menu_item_ids_by_day": {"$exists": True}})
        plans = await cursor.to_list(length=None)
        updated = 0

        for plan in plans:
            mapping = plan.get("menu_item_ids_by_day") or {}
            changed = False

            for day, item_ids in mapping.items():
                if not isinstance(item_ids, list):
                    continue
                day_changed = False
                new_ids: List[str] = []
                for item_id in item_ids:
                    replacement = replacements.get(str(item_id))
                    if replacement:
                        new_ids.append(replacement)
                        day_changed = True
                    else:
                        new_ids.append(str(item_id))

                if day_changed:
                    mapping[day] = self._deduplicate_ordered(new_ids)
                    changed = True

            if changed:
                await self.meal_plans.update_one(
                    {"_id": plan["_id"]},
                    {
                        "$set": {
                            "menu_item_ids_by_day": mapping,
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )
                updated += 1

        return updated

    async def _replace_ids_in_meal_subscriptions(self, replacements: Dict[str, str]) -> int:
        """Update active meal subscriptions so their slots point to consolidated IDs."""
        if self.meal_subscriptions is None or not replacements:
            return 0

        cursor = self.meal_subscriptions.find({"delivery_slots": {"$exists": True, "$ne": []}})
        subscriptions = await cursor.to_list(length=None)
        updated = 0

        for subscription in subscriptions:
            slots = subscription.get("delivery_slots") or []
            subscription_changed = False

            for slot in slots:
                slot_items = slot.get("menu_items") or {}
                if not isinstance(slot_items, dict) or not slot_items:
                    continue

                new_slot_items: Dict[str, int] = {}
                slot_changed = False

                for item_id, quantity in slot_items.items():
                    str_id = str(item_id)
                    replacement = replacements.get(str_id)
                    if replacement:
                        slot_changed = True
                        subscription_changed = True
                        new_slot_items[replacement] = new_slot_items.get(replacement, 0) + quantity
                    else:
                        new_slot_items[str_id] = new_slot_items.get(str_id, 0) + quantity

                if slot_changed:
                    slot["menu_items"] = new_slot_items

            if subscription_changed:
                await self.meal_subscriptions.update_one(
                    {"_id": subscription["_id"]},
                    {"$set": {"delivery_slots": slots, "updated_at": datetime.utcnow()}},
                )
                updated += 1

        return updated

    async def _update_menu_item_references(self, replacements: Dict[str, str]) -> None:
        """Ensure related collections reference the surviving menu item IDs."""
        if not replacements:
            return

        await self._replace_ids_in_weekly_schedule(replacements)
        await self._replace_ids_in_meal_plans(replacements)
        await self._replace_ids_in_meal_subscriptions(replacements)

    async def consolidate_program_variants(self) -> int:
        """Merge legacy duplicate menu items created for individual programs."""
        if self.menu_items is None:
            logger.warning("Menu items collection not available")
            return 0

        try:
            cursor = self.menu_items.find({})
            documents = await cursor.to_list(length=None)
            if not documents:
                return 0

            grouped: Dict[Tuple[str, str, float, str], List[Dict[str, Any]]] = {}
            for doc in documents:
                key = self._build_variant_group_key(doc)
                grouped.setdefault(key, []).append(doc)

            replacements: Dict[str, str] = {}
            keep_updates: Dict[str, Dict[str, Any]] = {}
            duplicates_to_delete: List[ObjectId] = []

            for variant_docs in grouped.values():
                if len(variant_docs) < 2:
                    continue

                has_daily_variant = any(doc.get("is_available_for_daily") for doc in variant_docs)
                has_meal_variant = any(doc.get("is_available_for_meal_plan") for doc in variant_docs)

                # Only consolidate variants that represent both availability scopes
                if not (has_daily_variant and has_meal_variant):
                    continue

                variant_docs.sort(
                    key=lambda doc: doc.get("created_at")
                    if isinstance(doc.get("created_at"), datetime)
                    else datetime.min
                )

                combined_daily = has_daily_variant
                combined_meal = has_meal_variant
                combined_available = any(doc.get("is_available", True) for doc in variant_docs)

                keep_doc = next(
                    (
                        doc
                        for doc in variant_docs
                        if doc.get("is_available_for_daily") and doc.get("is_available_for_meal_plan")
                    ),
                    None,
                )

                if keep_doc is None:
                    keep_doc = next(
                        (doc for doc in variant_docs if doc.get("is_available_for_daily")),
                        variant_docs[0],
                    )

                keep_id = keep_doc["_id"]
                updates: Dict[str, Any] = {}

                if keep_doc.get("is_available_for_daily", False) != combined_daily:
                    updates["is_available_for_daily"] = combined_daily
                if keep_doc.get("is_available_for_meal_plan", False) != combined_meal:
                    updates["is_available_for_meal_plan"] = combined_meal
                if keep_doc.get("is_available", True) != combined_available:
                    updates["is_available"] = combined_available

                if updates:
                    keep_updates[str(keep_id)] = updates

                for doc in variant_docs:
                    if doc["_id"] == keep_id:
                        continue
                    replacements[str(doc["_id"])] = str(keep_id)
                    duplicates_to_delete.append(doc["_id"])

            if not replacements:
                return 0

            await self._update_menu_item_references(replacements)

            for keep_id_str, payload in keep_updates.items():
                payload["updated_at"] = datetime.utcnow()
                await self.menu_items.update_one(
                    {"_id": ObjectId(keep_id_str)},
                    {"$set": payload},
                )

            if duplicates_to_delete:
                await self.menu_items.delete_many({"_id": {"$in": duplicates_to_delete}})

            logger.info(
                "Consolidated %d legacy program-specific menu item variants",
                len(duplicates_to_delete),
            )
            return len(duplicates_to_delete)
        except Exception as exc:
            logger.error(
                "Failed to consolidate legacy menu item variants: %s",
                exc,
                exc_info=True,
            )
            return 0

    async def _fetch_daily_items_with_addons_last(
        self,
        base_query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Return all daily items with add-ons appended at the end."""
        regex_condition = self._addons_regex_condition()
        non_addons_query = {**base_query, "category": {"$not": regex_condition}}
        addons_query = {**base_query, "category": regex_condition}

        non_cursor = self.menu_items.find(non_addons_query).sort("name", 1)
        addons_cursor = self.menu_items.find(addons_query).sort("name", 1)

        non_items = await non_cursor.to_list(length=None)
        addon_items = await addons_cursor.to_list(length=None)
        return non_items + addon_items

    async def _fetch_daily_items_with_addons_last_paginated(
        self,
        base_query: Dict[str, Any],
        skip: int,
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return a paginated slice while keeping add-ons last overall."""
        regex_condition = self._addons_regex_condition()
        non_addons_query = {**base_query, "category": {"$not": regex_condition}}
        addons_query = {**base_query, "category": regex_condition}

        total = await self.menu_items.count_documents(base_query)
        if total == 0 or skip >= total:
            return [], total

        non_total = await self.menu_items.count_documents(non_addons_query)
        items: List[Dict[str, Any]] = []
        remaining_limit = limit
        remaining_skip = skip

        if non_total > 0 and remaining_limit > 0:
            if remaining_skip < non_total:
                non_skip = remaining_skip
                non_limit = min(remaining_limit, non_total - non_skip)
                non_cursor = (
                    self.menu_items.find(non_addons_query)
                    .sort("name", 1)
                    .skip(non_skip)
                    .limit(non_limit)
                )
                non_items = await non_cursor.to_list(length=non_limit)
                items.extend(non_items)
                remaining_limit -= non_limit
                remaining_skip = 0
            else:
                remaining_skip -= non_total

        if remaining_limit > 0:
            addon_cursor = (
                self.menu_items.find(addons_query)
                .sort("name", 1)
                .skip(max(0, remaining_skip))
                .limit(remaining_limit)
            )
            addon_items = await addon_cursor.to_list(length=remaining_limit)
            items.extend(addon_items)

        return items, total

    @property
    def db(self):
        """Get database instance lazily"""
        return database.db

    @property
    def menu_items(self):
        """Get menu_items collection"""
        if self.db is not None:
            return self.db.menu_items
        return None

    @property
    def categories(self):
        """Get categories collection"""
        if self.db is not None:
            return self.db.categories
        return None

    @property
    def weekly_schedule(self):
        """Get weekly_menu_schedule collection"""
        if self.db is not None:
            return self.db.weekly_menu_schedule
        return None

    @property
    def meal_plans(self):
        """Get meal subscription plans collection"""
        if self.db is not None and hasattr(self.db, "meal_subscription_plans"):
            return self.db.meal_subscription_plans
        return None

    @property
    def meal_subscriptions(self):
        """Get meal subscriptions collection"""
        if self.db is not None and hasattr(self.db, "meal_subscriptions"):
            return self.db.meal_subscriptions
        return None

    # ============= CATEGORY MANAGEMENT METHODS =============

    async def create_category(self, category_data: dict) -> CategoryModel:
        """Create new category"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Check if category with same name exists
            existing = await self.categories.find_one({"name": category_data["name"]})
            if existing:
                raise ValueError(f"Category with name '{category_data['name']}' already exists")

            # Set default sort order if not provided
            if "sort_order" not in category_data or category_data["sort_order"] is None:
                highest = await self.categories.find_one(sort=[("sort_order", -1)])
                category_data["sort_order"] = (highest["sort_order"] + 1) if highest else 1

            # Prepare category document
            category_dict = {
                **category_data,
                "is_active": category_data.get("is_active", True),
                "created_at": datetime.utcnow()
            }

            result = await self.categories.insert_one(category_dict)
            # FIX: Convert ObjectId to string
            category_dict["_id"] = str(result.inserted_id)

            logger.info(f"Category created: {category_data['name']} with ID {result.inserted_id}")
            return CategoryModel(**category_dict)

        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise

    async def update_category(self, category_id: str, update_data: dict) -> Optional[CategoryModel]:
        """Update existing category"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(category_id):
                raise ValueError(f"Invalid category ID format: {category_id}")

            cleaned_data: Dict[str, Any] = {}
            for key, value in update_data.items():
                if value is None:
                    if key == "image_url":
                        cleaned_data[key] = None
                    continue
                cleaned_data[key] = value

            if not cleaned_data:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            if not update_data:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            if not update_data:
                return await self.get_category_by_id(category_id)

            result = await self.categories.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Category not found or no changes made: {category_id}")
                return None

            # Get and return updated category
            category = await self.get_category_by_id(category_id)
            logger.info(f"Category updated: {category_id}")
            return category

        except Exception as e:
            logger.error(f"Error updating category: {e}")
            raise

    async def delete_category(self, category_id: str, permanent: bool = False) -> bool:
        """Delete category (soft delete by default)"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(category_id):
                logger.error(f"Invalid category ID format: {category_id}")
                return False

            if permanent:
                # Permanent delete
                result = await self.categories.delete_one({"_id": ObjectId(category_id)})
                success = result.deleted_count > 0
                if success:
                    logger.info(f"Category permanently deleted: {category_id}")
            else:
                # Soft delete (deactivate)
                result = await self.categories.update_one(
                    {"_id": ObjectId(category_id)},
                    {"$set": {"is_active": False}}
                )
                success = result.modified_count > 0
                if success:
                    logger.info(f"Category deactivated: {category_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False

    async def get_category_by_id(self, category_id: str) -> Optional[CategoryModel]:
        """Get category by ID or name"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return None

            # Check if category_id is ObjectId or string (name)
            if ObjectId.is_valid(category_id):
                category = await self.categories.find_one({"_id": ObjectId(category_id)})
            else:
                # Try to find by name
                category = await self.categories.find_one({"name": category_id})

            if category:
                # Convert ObjectId to string for the model
                if "_id" in category and isinstance(category["_id"], ObjectId):
                    category["_id"] = str(category["_id"])
                return CategoryModel(**category)
            return None

        except Exception as e:
            logger.error(f"Error getting category by ID: {e}")
            return None

    async def get_all_categories(self, include_inactive: bool = False) -> List[CategoryModel]:
        """Get all categories (with option to include inactive)"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return []

            query = {} if include_inactive else {"is_active": True}
            cursor = self.categories.find(query).sort("sort_order", 1)
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []

    async def get_all_categories_paginated(self, include_inactive: bool, skip: int, limit: int):
        """Paginated categories with total count."""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return [], 0

            query = {} if include_inactive else {"is_active": True}
            total = await self.categories.count_documents(query)
            cursor = self.categories.find(query).sort("sort_order", 1).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting paginated categories: {e}")
            return [], 0

    async def update_category_order(self, category_id: str, new_order: int) -> bool:
        """Update category sort order"""
        try:
            if self.categories is None:
                raise ValueError("Categories collection not available")

            if not ObjectId.is_valid(category_id):
                return False

            # Update the sort order
            result = await self.categories.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": {"sort_order": new_order}}
            )

            success = result.modified_count > 0
            if success:
                logger.info(f"Category order updated: {category_id} -> {new_order}")

            return success

        except Exception as e:
            logger.error(f"Error updating category order: {e}")
            return False

    async def category_has_items(self, category_id: str) -> bool:
        """Check if category has associated menu items"""
        try:
            if self.menu_items is None or self.categories is None:
                return False

            # Get category by ID or name
            category = await self.get_category_by_id(category_id)
            if not category:
                return False

            # Check for menu items with this category
            count = await self.menu_items.count_documents({"category": category.name})
            return count > 0

        except Exception as e:
            logger.error(f"Error checking category items: {e}")
            return False

    # ============= MENU ITEM METHODS =============

    async def get_all_menu_items(self, include_unavailable: bool = False, category: Optional[str] = None) -> List[MenuItemModel]:
        """Get all menu items (admin view)"""
        try:
            await self.consolidate_program_variants()

            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            query = {}
            if not include_unavailable:
                query["is_available"] = True
            if category:
                query["category"] = category

            cursor = self.menu_items.find(query).sort([("category", 1), ("name", 1)])
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting all menu items: {e}")
            return []

    async def get_all_menu_items_paginated(
        self,
        include_unavailable: bool,
        category: Optional[str],
        skip: int,
        limit: int,
        search: Optional[str] = None,
    ):
        """Paginated menu items with total count (admin view)."""
        try:
            await self.consolidate_program_variants()

            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return [], 0

            query = {}
            if not include_unavailable:
                query["is_available"] = True
            if category:
                query["category"] = category
            if search:
                search_term = search.strip()
                if search_term:
                    regex = {"$regex": search_term, "$options": "i"}
                    query["$or"] = [
                        {"name": regex},
                        {"description": regex},
                    ]

            total = await self.menu_items.count_documents(query)
            cursor = self.menu_items.find(query).sort([("category", 1), ("name", 1)]).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting paginated menu items: {e}")
            return [], 0

    async def get_menu_items_stats(self) -> Dict[str, int]:
        """Return aggregate counts for admin dashboard cards."""
        if self.menu_items is None:
            return {
                "total": 0,
                "available": 0,
                "unavailable": 0,
                "daily_ready": 0,
                "weekly_ready": 0,
            }

        base_query: Dict[str, Any] = {}
        total = await self.menu_items.count_documents(base_query)

        available_query = {**base_query, "is_available": True}
        available = await self.menu_items.count_documents(available_query)

        daily_ready_query = {**available_query, "is_available_for_daily": True}
        daily_ready = await self.menu_items.count_documents(daily_ready_query)

        weekly_ready_query = {**available_query, "is_available_for_meal_plan": True}
        weekly_ready = await self.menu_items.count_documents(weekly_ready_query)

        return {
            "total": total,
            "available": available,
            "unavailable": max(total - available, 0),
            "daily_ready": daily_ready,
            "weekly_ready": weekly_ready,
        }

    def _build_daily_menu_query(
        self,
        category: Optional[str] = None,
        is_vegetarian: Optional[bool] = None,
        is_vegan: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {
            "is_available": True,
            "is_available_for_daily": True,
        }
        if category:
            query["category"] = category
        if is_vegetarian is not None:
            query["is_vegetarian"] = is_vegetarian
        if is_vegan is not None:
            query["is_vegan"] = is_vegan
        if search:
            search_term = search.strip()
            if search_term:
                regex = {"$regex": search_term, "$options": "i"}
                query["$or"] = [
                    {"name": regex},
                    {"description": regex},
                ]
        return query

    async def get_daily_menu(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MenuItemModel]:
        """Get daily menu items with optional filters"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            filters = filters or {}
            query = self._build_daily_menu_query(
                category=filters.get("category"),
                is_vegetarian=filters.get("is_vegetarian"),
                is_vegan=filters.get("is_vegan"),
                search=filters.get("search"),
            )

            if filters.get("category"):
                cursor = self.menu_items.find(query).sort("name", 1)
                items = await cursor.to_list(length=None)
            else:
                items = await self._fetch_daily_items_with_addons_last(query)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting daily menu: {e}")
            raise

    async def get_daily_menu_paginated(
        self,
        filters: Optional[Dict[str, Any]],
        skip: int,
        limit: int,
    ) -> Tuple[List[MenuItemModel], int]:
        """Get daily menu items with pagination and total count."""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return [], 0

            filters = filters or {}
            query = self._build_daily_menu_query(
                category=filters.get("category"),
                is_vegetarian=filters.get("is_vegetarian"),
                is_vegan=filters.get("is_vegan"),
                search=filters.get("search"),
            )

            if filters.get("category"):
                total = await self.menu_items.count_documents(query)
                cursor = (
                    self.menu_items.find(query).sort("name", 1).skip(skip).limit(limit)
                )
                items = await cursor.to_list(length=limit)
            else:
                items, total = await self._fetch_daily_items_with_addons_last_paginated(
                    query, skip, limit
                )

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items], total
        except Exception as e:
            logger.error(f"Error getting daily menu (paginated): {e}")
            return [], 0

    async def _get_default_weekly_items(self, limit: int = 18) -> List[MenuItemModel]:
        """Return a generic list of weekly-available menu items (used as fallback)."""
        if self.menu_items is None:
            return []

        cursor = (
            self.menu_items.find(
                {
                    "is_available": True,
                    "is_available_for_meal_plan": True,
                }
            )
            .sort([("updated_at", -1), ("name", 1)])
            .limit(limit)
        )
        items = await cursor.to_list(length=limit)
        for item in items:
            if "_id" in item and isinstance(item["_id"], ObjectId):
                item["_id"] = str(item["_id"])
        return [MenuItemModel(**item) for item in items]

    async def get_weekly_menu(self, delivery_date: str) -> Optional[dict]:
        """Get weekly menu for specific delivery date (falls back to generic items if needed)."""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available for weekly menu")
                return None

            date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
            schedule = None
            if self.weekly_schedule is not None:
                schedule = await self.weekly_schedule.find_one(
                    {"delivery_date": date_obj, "is_active": True}
                )
            else:
                logger.warning("Weekly schedule collection missing; using fallback items")

            items: List[MenuItemModel] = []
            if schedule:
                item_ids = [
                    ObjectId(item_id) if isinstance(item_id, str) else item_id
                    for item_id in schedule.get("menu_items", [])
                ]

                if item_ids:
                    cursor = self.menu_items.find(
                        {
                            "_id": {"$in": item_ids},
                            "is_available": True,
                            "is_available_for_meal_plan": True,
                        }
                    )
                    raw_items = await cursor.to_list(length=None)
                    for item in raw_items:
                        if "_id" in item and isinstance(item["_id"], ObjectId):
                            item["_id"] = str(item["_id"])
                        items.append(MenuItemModel(**item))

            if not schedule:
                logger.info(
                    "No weekly schedule found for %s; serving fallback weekly items",
                    delivery_date,
                )

            if not items:
                fallback_items = await self._get_default_weekly_items()
                if not fallback_items:
                    logger.warning(
                        "Unable to build fallback weekly menu for %s (no weekly items found)",
                        delivery_date,
                    )
                    return None
                items = fallback_items

            return {
                "delivery_date": delivery_date,
                "menu_rotation": schedule.get("menu_rotation", 1) if schedule else 0,
                "items": items,
            }

        except Exception as e:
            logger.error(f"Error getting weekly menu: {e}")
            raise

    async def get_catering_menu(self) -> List[MenuItemModel]:
        """Catering menu has been discontinued; return an empty list."""
        logger.info("Catering menu request received; returning empty list.")
        return []

    async def get_catering_menu_paginated(self, skip: int, limit: int) -> List[MenuItemModel]:
        """Catering menu has been discontinued; return an empty list."""
        logger.info(
            "Paginated catering menu request received (skip=%s, limit=%s); returning empty list.",
            skip,
            limit,
        )
        return []

    async def get_menu_item_by_id(self, item_id: str) -> Optional[MenuItemModel]:
        """Get specific menu item by ID"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return None

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                logger.error(f"Invalid ObjectId format: {item_id}")
                return None

            item = await self.menu_items.find_one({"_id": ObjectId(item_id)})
            if item:
                # Convert ObjectId to string
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])
                return MenuItemModel(**item)
            return None

        except Exception as e:
            logger.error(f"Error getting menu item by ID: {e}")
            return None

    async def get_menu_items_by_ids(self, item_ids: List[str]) -> List[MenuItemModel]:
        """Get multiple menu items by their IDs without filtering availability."""
        try:
            if self.menu_items is None or not item_ids:
                logger.warning("Menu items collection not available or no IDs provided")
                return []

            valid_ids = []
            for item_id in item_ids:
                if ObjectId.is_valid(item_id):
                    valid_ids.append(ObjectId(item_id))
                else:
                    logger.warning(f"Skipping invalid menu item ID: {item_id}")

            if not valid_ids:
                return []

            cursor = self.menu_items.find({"_id": {"$in": valid_ids}})
            items = await cursor.to_list(length=None)

            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting menu items by IDs: {e}")
            return []

    async def create_menu_item(
        self, item_data: dict, image_url: Optional[str] = None
    ) -> MenuItemModel:
        """Create a single menu item that can be available across multiple programs."""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            available_for_daily = bool(item_data.get("is_available_for_daily"))
            available_for_weekly = bool(item_data.get("is_available_for_meal_plan"))

            if not available_for_daily and not available_for_weekly:
                raise ValueError("At least one availability option must be selected")

            base_fields = {
                key: value
                for key, value in item_data.items()
                if key not in {"is_available_for_daily", "is_available_for_meal_plan"}
            }
            base_fields.setdefault("allergens", [])
            base_fields.setdefault("is_vegetarian", False)
            base_fields.setdefault("is_halal", True)

            now = datetime.utcnow()

            payload: Dict[str, Any] = {
                **base_fields,
                "is_available_for_daily": available_for_daily,
                "is_available_for_meal_plan": available_for_weekly,
                "is_available": base_fields.get("is_available", True),
                "created_at": now,
                "updated_at": now,
            }

            if "allergens" in payload:
                if isinstance(payload["allergens"], list):
                    payload["allergens"] = [
                        str(allergen).strip()
                        for allergen in payload["allergens"]
                        if str(allergen).strip()
                    ]
                else:
                    payload["allergens"] = []
            else:
                payload["allergens"] = []

            if image_url is not None:
                payload["image_url"] = image_url
            elif "image_url" not in payload:
                payload["image_url"] = None

            result = await self.menu_items.insert_one(payload)
            payload["_id"] = str(result.inserted_id)
            logger.info(
                "Menu item created: %s (ID: %s)",
                item_data.get("name"),
                result.inserted_id,
            )
            return MenuItemModel(**payload)

        except Exception as e:
            logger.error(f"Error creating menu item: {e}")
            raise

    async def update_menu_item(self, item_id: str, update_data: dict) -> Optional[MenuItemModel]:
        """Update existing menu item"""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                raise ValueError(f"Invalid item ID format: {item_id}")

            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            update_payload: Dict[str, Any] = {}
            for key, value in update_data.items():
                if value is None:
                    if key == "image_url":
                        update_payload[key] = None
                    continue
                update_payload[key] = value

            if not update_payload:
                logger.warning("No update fields provided for menu item %s", item_id)
                return await self.get_menu_item_by_id(item_id)

            result = await self.menu_items.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_payload}
            )

            if result.matched_count == 0:
                logger.warning(f"Menu item not found: {item_id}")
                return None

            # Get and return updated item
            item = await self.get_menu_item_by_id(item_id)
            logger.info(f"Menu item updated: {item_id}")
            return item

        except Exception as e:
            logger.error(f"Error updating menu item: {e}")
            raise

    async def delete_menu_item(self, item_id: str) -> bool:
        """Permanently delete a menu item."""
        try:
            if self.menu_items is None:
                raise ValueError("Menu items collection not available")

            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                logger.error(f"Invalid item ID format: {item_id}")
                return False

            result = await self.menu_items.delete_one({"_id": ObjectId(item_id)})

            success = result.deleted_count > 0
            if success:
                logger.info(f"Menu item permanently deleted: {item_id}")
            else:
                logger.warning(f"Menu item not found for deletion: {item_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting menu item: {e}")
            return False

    # ============= WEEKLY SCHEDULE METHODS =============

    async def create_weekly_menu_schedule(self, delivery_date: str, menu_rotation: int, menu_item_ids: List[str]) -> WeeklyMenuScheduleModel:
        """Create or update weekly menu schedule"""
        try:
            if self.weekly_schedule is None:
                raise ValueError("Weekly schedule collection not available")

            date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")

            # Validate menu items exist
            item_object_ids = []
            for item_id in menu_item_ids:
                if not ObjectId.is_valid(item_id):
                    raise ValueError(f"Invalid menu item ID: {item_id}")
                item_object_ids.append(ObjectId(item_id))

            # Check if items exist
            if self.menu_items is not None:
                existing_count = await self.menu_items.count_documents({
                    "_id": {"$in": item_object_ids}
                })

                if existing_count != len(item_object_ids):
                    raise ValueError("Some menu items do not exist")

            # Create or update schedule
            schedule_dict = {
                "delivery_date": date_obj,
                "menu_rotation": menu_rotation,
                "menu_items": item_object_ids,
                "is_active": True,
                "created_at": datetime.utcnow()
            }

            # Use upsert to create or update
            result = await self.weekly_schedule.update_one(
                {"delivery_date": date_obj},
                {"$set": schedule_dict},
                upsert=True
            )

            if result.upserted_id:
                # FIX: Convert ObjectId to string
                schedule_dict["_id"] = str(result.upserted_id)
                logger.info(f"Weekly schedule created for {delivery_date}")
            else:
                # Get the existing document
                schedule = await self.weekly_schedule.find_one({"delivery_date": date_obj})
                if schedule:
                    # Convert ObjectId to string
                    if "_id" in schedule and isinstance(schedule["_id"], ObjectId):
                        schedule["_id"] = str(schedule["_id"])
                    schedule_dict = schedule
                logger.info(f"Weekly schedule updated for {delivery_date}")

            return WeeklyMenuScheduleModel(**schedule_dict)

        except Exception as e:
            logger.error(f"Error creating weekly menu schedule: {e}")
            raise

    # ============= UTILITY METHODS =============

    async def get_categories(self) -> List[CategoryModel]:
        """Get all active food categories (public endpoint - alias for consistency)"""
        try:
            if self.categories is None:
                logger.warning("Categories collection not available")
                return []

            cursor = self.categories.find({"is_active": True}).sort("sort_order", 1)
            items = await cursor.to_list(length=None)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [CategoryModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise

    async def search_menu_items(self, query: str, category: Optional[str] = None) -> List[MenuItemModel]:
        """Search menu items by name or description"""
        try:
            if self.menu_items is None:
                logger.warning("Menu items collection not available")
                return []

            # Build search query
            search_filter = {
                "is_available": True,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }

            if category:
                search_filter["category"] = category

            cursor = self.menu_items.find(search_filter).sort("name", 1).limit(20)
            items = await cursor.to_list(length=20)

            # Convert ObjectIds to strings
            for item in items:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return [MenuItemModel(**item) for item in items]

        except Exception as e:
            logger.error(f"Error searching menu items: {e}")
            return []

# Create service instance (singleton)
menu_service = MenuService()
```

---

#### 📄 notification_service.py
**Path:** `app\services\notification_service.py`

```python
import httpx
import logging
from bson import ObjectId

from app.config.settings import settings
from app.models.order import OrderModel
from app.models.catering import CateringOrderModel
from app.services.auth_service import auth_service
from app.services.subscription_service import meal_subscription_service
from app.services.email_service import send_order_confirmation_email
from app.utils.constants import OrderType

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    async def _build_subscription_summary(self, order: OrderModel) -> str:
        """Compose a short summary of the meal subscription linked to the order."""
        if (
            not order.id
            or meal_subscription_service.subscriptions is None
        ):
            return ""

        try:
            subscription = await meal_subscription_service.subscriptions.find_one(
                {"order_id": ObjectId(order.id)}
            )
        except Exception as exc:
            logger.warning(
                "Unable to load subscription for order %s: %s",
                order.order_number,
                exc,
            )
            return ""

        if not subscription:
            return ""

        plan_lines = []
        for plan in subscription.get("plan_selections", []):
            plan_name = plan.get("plan_name") or plan.get("plan_code")
            quantity = plan.get("quantity", 1)
            included = plan.get("included_meals", 0)
            deliveries_in_cycle = plan.get("deliveries_in_cycle") or len(
                subscription.get("delivery_slots", [])
            )
            plan_lines.append(
                f"  • {plan_name} x{quantity} ({included} meals, {deliveries_in_cycle} deliveries)"
            )
            delivery_days = plan.get("available_delivery_days") or []
            if delivery_days:
                plan_lines.append(
                    f"     Days: {', '.join(day.title() for day in delivery_days)}"
                )

        delivery_lines = []
        for slot in subscription.get("delivery_slots", []):
            raw_date = slot.get("delivery_date")
            if hasattr(raw_date, "strftime"):
                date_str = raw_date.strftime("%d %b")
            else:
                date_str = str(raw_date)
            total_boxes = sum((slot.get("menu_items") or {}).values())
            delivery_lines.append(f"  • {date_str}: {total_boxes} box(es)")

        reminder_line = ""
        reminder_settings = subscription.get("reminder_settings")
        if reminder_settings and reminder_settings.get("enabled"):
            frequency = reminder_settings.get("frequency_days", 7)
            channel = reminder_settings.get("channel", "in_app").replace("_", " ").title()
            reminder_line = f"Reminders: every {frequency} day(s) via {channel}"

        sections = []
        if plan_lines:
            sections.append("*Plan Details:*\n" + "\n".join(plan_lines))
        if delivery_lines:
            sections.append("*Scheduled Deliveries:*\n" + "\n".join(delivery_lines))
        if reminder_line:
            sections.append(reminder_line)

        return "\n".join(sections)
    
    async def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message via Business API"""
        try:
            # Clean phone number
            phone = phone_number.replace(" ", "").replace("-", "")
            if phone.startswith("0"):
                phone = "+61" + phone[1:]
            elif not phone.startswith("+"):
                phone = "+61" + phone
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"WhatsApp message sent to {phone}")
                    return True
                else:
                    logger.error(f"Failed to send WhatsApp message: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_order_confirmation(self, order: OrderModel) -> bool:
        """Send order confirmation notification"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False

            item_lines = [
                f"- {item.item_name} x{item.quantity} - ${item.subtotal:.2f}"
                for item in order.items
            ]

            delivery_lines = []
            if order.delivery_method != "pickup" and order.delivery_address:
                addr = order.delivery_address
                street = addr.get("street") if isinstance(addr, dict) else getattr(addr, "street", "")
                suburb = addr.get("suburb") if isinstance(addr, dict) else getattr(addr, "suburb", "")
                postcode = addr.get("postcode") if isinstance(addr, dict) else getattr(addr, "postcode", "")
                if street:
                    delivery_lines.append(street)
                city_line = " ".join(value for value in [suburb, postcode] if value)
                if city_line:
                    delivery_lines.append(city_line.strip())

            subscription_summary = ""
            if order.order_type == OrderType.MEAL_SUBSCRIPTION.value:
                subscription_summary = await self._build_subscription_summary(order)

            message_lines = [
                "*Order Confirmed!*",
                "",
                "Thank you for your order at Bakar's Food & Catering!",
                "",
                "*Order Details:*",
                f"Order Number: {order.order_number}",
                f"Order Type: {order.order_type.title()}",
            ]

            if item_lines:
                message_lines.extend(["", "*Items:*", *item_lines])

            message_lines.extend(
                [
                    "",
                    "*Payment Summary:*",
                    f"Subtotal: ${order.subtotal:.2f}",
                    f"Delivery Fee: ${order.delivery_fee:.2f}",
                    f"Total: ${order.total_amount:.2f}",
                ]
            )

            if delivery_lines:
                message_lines.extend(["", "Delivery Address:", *delivery_lines])

            if subscription_summary:
                message_lines.extend(["", subscription_summary])

            message_lines.extend(
                [
                    "",
                    f"Status: {order.status.title()}",
                    "",
                    "We'll notify you when your order is ready!",
                    "",
                    "For any queries, contact us:",
                    "Phone: [Your Phone Number]",
                    "Email: [Your Email]",
                    "",
                    "Thank you for choosing Bakar's Food & Catering!",
                ]
            )

            message = "\n".join(message_lines)

            email_sent = False
            customer_name = " ".join(filter(None, [getattr(user, "first_name", ""), getattr(user, "last_name", "")])).strip()
            customer_email = getattr(user, "email", None)

            if customer_email:
                try:
                    await send_order_confirmation_email(
                        order=order,
                        customer_email=customer_email,
                        customer_name=customer_name or customer_email.split("@")[0],
                        restaurant_email=settings.ORDER_NOTIFICATIONS_EMAIL,
                    )
                    email_sent = True
                except Exception as email_error:
                    logger.error("Failed to send order confirmation email: %s", email_error)

            whatsapp_sent = False
            whatsapp_configured = all([self.api_url, self.access_token, self.phone_number_id])
            if whatsapp_configured and getattr(user, "phone", None):
                whatsapp_sent = await self.send_whatsapp_message(user.phone, message)

            return whatsapp_sent or email_sent

        except Exception as e:
            logger.error(f"Error sending order confirmation: {e}")
            return False


    async def send_catering_quote(self, order: OrderModel, catering: CateringOrderModel) -> bool:
        """Send catering quote via WhatsApp"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False
            
            event_date = catering.event_date.strftime("%d %B %Y")

            message_lines = [
                "📋 *Catering Quote*",
                "",
                "Thank you for choosing Bakar's Food & Catering!",
                "",
                f"*Order Number:* {order.order_number}",
                "",
                "*Event Details:*",
                f"Date: {event_date}",
                f"Time: {catering.event_time or 'TBD'}",
                f"Venue: {catering.venue_address}",
                f"Guest Count: {catering.guest_count}",
                "",
                "*Package Selected:*",
                f"{catering.package_type.title()} Package",
                f"Price: ${catering.package_price_per_head}/head",
                "",
                "*Pricing Breakdown:*",
                f"Package Total: ${catering.package_total:.2f}",
                f"Delivery Fee: ${catering.delivery_fee:.2f}",
                f"Total Amount: ${order.total_amount:.2f}",
                "",
                "*Payment Terms:*",
                f"Advance Payment (50%): ${catering.advance_payment_amount:.2f}",
                f"Balance Payment: ${catering.remaining_payment_amount:.2f}",
                "",
                "Special Requests:",
                catering.special_requests or "None",
                "",
                "Please confirm your booking by paying the advance amount.",
                "",
                "For any changes or queries, contact us:",
                "📞 [Your Phone Number]",
                "📧 [Your Email]",
                "",
                "We look forward to catering your event! 🎊",
            ]

            message = "\n".join(message_lines)

            return await self.send_whatsapp_message(user.phone, message)
            
        except Exception as e:
            logger.error(f"Error sending catering quote: {e}")
            return False
    
    async def send_status_update(self, order: OrderModel, new_status: str) -> bool:
        """Send order status update"""
        try:
            user = await auth_service.get_user_by_id(str(order.user_id))
            if not user:
                return False
            
            status_messages = {
                "confirmed": "Your order has been confirmed and is being prepared! 👨‍🍳",
                "preparing": "Your order is being prepared with love! 🔥",
                "out_for_delivery": "Your order is on the way! 🚗",
                "delivered": "Your order has been delivered! Enjoy your meal! 😋",
                "cancelled": "Your order has been cancelled. Contact us for details. ℹ️",
            }

            message_lines = [
                "*Order Status Update*",
                "",
                f"Order Number: {order.order_number}",
                "",
                f"Status: {new_status.title().replace('_', ' ')}",
            ]

            status_note = status_messages.get(new_status)
            if status_note:
                message_lines.append(status_note)

            message_lines.extend(
                [
                    "",
                    "Track your order: [Your tracking URL]",
                    "",
                    "Thank you for choosing Bakar's Food & Catering! 🍛",
                ]
            )

            message = "\n".join(message_lines)

            return await self.send_whatsapp_message(user.phone, message)
            
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
            return False

notification_service = NotificationService()
```

---

#### 📄 order_service.py
**Path:** `app\services\order_service.py`

```python
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from app.config.database import get_database
from app.models.order import OrderModel, OrderItem
from app.models.subscription import MealSubscriptionModel, MealPlanSelection, DeliverySlotSelection
from app.models.catering import CateringOrderModel
from app.utils.helpers import generate_order_number, parse_date
from app.utils.constants import (
    OrderType, OrderStatus, PaymentStatus,
    DAILY_DELIVERY_FEE,
    REGULAR_DELIVERY_MIN_BOXES,
    REGULAR_PICKUP_MIN_BOXES,
    DEFAULT_EXTRA_BOX_PRICE,
    CATERING_BASIC_PRICE, CATERING_PREMIUM_PRICE, CATERING_DIAMOND_PRICE,
    CATERING_ADVANCE_PAYMENT_PERCENT, CATERING_BASE_DELIVERY_FEE
)
from app.services.menu_service import menu_service
from app.services.delivery_service import delivery_service
from app.services.subscription_service import meal_subscription_service
from app.services.reminder_service import reminder_service
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self._db = None
        self._orders = None
        self._meal_subs = None
        self._legacy_weekly_subs = None
        self._catering_orders = None
    
    @property
    def db(self):
        """Get database instance lazily"""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def orders(self):
        """Get orders collection lazily"""
        if self._orders is None and self.db is not None:
            self._orders = self.db.orders
        return self._orders
    
    @property
    def meal_subs(self):
        """Get meal_subscriptions collection lazily"""
        if self._meal_subs is None and self.db is not None:
            self._meal_subs = self.db.meal_subscriptions
        return self._meal_subs
    
    @property
    def weekly_subs_legacy(self):
        """Access legacy weekly subscription collection if still present."""
        if self._legacy_weekly_subs is None and self.db is not None:
            self._legacy_weekly_subs = getattr(self.db, "weekly_subscriptions", None)
        return self._legacy_weekly_subs
    
    @property
    def catering_orders(self):
        """Get catering_orders collection lazily"""
        if self._catering_orders is None and self.db is not None:
            self._catering_orders = self.db.catering_orders
        return self._catering_orders
    
    async def create_daily_order(
        self,
        user_id: str,
        items: List[Dict],
        delivery_method: str,
        delivery_address: dict,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
    ) -> OrderModel:
        """Create daily menu order"""
        try:
            if self.orders is None or self.db is None:
                raise ValueError("Database not connected")
                
            # Calculate order items
            order_items = []
            subtotal = 0.0
            
            normalized_items = [
                item_data.dict() if hasattr(item_data, "dict") else item_data
                for item_data in items
            ]

            for item_data in normalized_items:
                item_id = item_data.get("item_id")
                quantity = item_data.get("quantity")

                if not item_id or not quantity:
                    raise ValueError("Invalid daily order items payload")
                
                menu_item = await menu_service.get_menu_item_by_id(item_id)
                if not menu_item or not menu_item.is_available_for_daily:
                    raise ValueError(f"Item {item_id} not available for daily orders")
                
                order_item = OrderItem(
                    item_id=str(menu_item.id),
                    item_name=menu_item.name,
                    category=menu_item.category,
                    quantity=quantity,
                    price=menu_item.price,
                    subtotal=menu_item.price * quantity
                )
                order_items.append(order_item)
                subtotal += order_item.subtotal
            
            # Calculate delivery fee
            delivery_fee = 0.0
            if delivery_method == "standard":
                # Check delivery availability
                address_str = f"{delivery_address['street']}, {delivery_address['suburb']}, {delivery_address['postcode']}"
                is_available, distance, geocoded, failure_reason = await delivery_service.check_daily_delivery(address_str)
                
                if not is_available:
                    message = failure_reason or "Daily delivery is restricted to addresses within 6km of Guildford."
                    logger.warning(f"Daily order blocked for address '{address_str}': {message}")
                    raise ValueError(message)
                
                delivery_fee = DAILY_DELIVERY_FEE
                if geocoded:
                    delivery_address["latitude"] = geocoded.get("latitude")
                    delivery_address["longitude"] = geocoded.get("longitude")
                    if geocoded.get("formatted_address"):
                        delivery_address["formatted_address"] = geocoded["formatted_address"]
            
            total_amount = subtotal + delivery_fee
            
            # Create order document for MongoDB
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),  # Store as ObjectId in MongoDB
                "order_type": OrderType.DAILY,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "payment_method": (payment_method or "cash").lower(),
                "items": [item.dict() for item in order_items],
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "total_amount": total_amount,
                "delivery_method": delivery_method,
                "delivery_address": delivery_address,
                "delivery_instructions": delivery_instructions,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id

            # Convert all ObjectIds to strings for the response model
            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),  # Convert ObjectId to string
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "subtotal": order_dict["subtotal"],
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "delivery_instructions": order_dict["delivery_instructions"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"]
            }

            logger.info(f"Daily order created: {order_dict['order_number']}")
            return OrderModel(**response_dict)
            
        except Exception as e:
            logger.error(f"Error creating daily order: {e}")
            raise

    async def _prepare_meal_subscription_documents(
        self,
        user_id: str,
        plan_selections: List[Dict[str, Any]],
        delivery_slots: List[Dict[str, Any]],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: Optional[str],
        notes: Optional[str],
        payment_method: str,
        delivery_address_id: Optional[str],
    ) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], int]:
        """Shared preparation logic for creating/updating meal subscription orders."""
        if not plan_selections:
            raise ValueError("At least one plan selection is required")

        if not delivery_slots:
            raise ValueError("Delivery schedule is required")

        fulfilment = (fulfilment_method or "delivery").lower()
        address_data = dict(delivery_address or {})

        plan_records: List[Dict[str, Any]] = []
        total_included_boxes = 0
        plan_base_total = 0.0
        max_boxes_per_meal_total = 0
        has_regular_plan = False
        has_subscription_plan = False

        for selection in plan_selections:
            plan_id = selection.get("plan_id")
            quantity = int(selection.get("quantity", 1))
            if quantity <= 0:
                raise ValueError("Plan quantity must be at least 1")

            plan = await meal_subscription_service.get_plan_by_id(plan_id)
            if not plan or not plan.is_active:
                raise ValueError("Selected meal subscription plan is not available")

            if not plan.allow_multiple and quantity > 1:
                raise ValueError(f"{plan.name} cannot be selected more than once")

            included_boxes = (plan.included_meals or 0) * quantity
            plan_price = (plan.price_per_plan or 0.0) * quantity

            if plan.max_boxes_per_meal:
                max_boxes_per_meal_total += plan.max_boxes_per_meal * quantity

            total_included_boxes += included_boxes
            plan_base_total += plan_price
            has_regular_plan = has_regular_plan or plan.tab == "regular"
            has_subscription_plan = has_subscription_plan or (plan.included_meals or 0) > 0

            plan_records.append(
                {
                    "plan": plan,
                    "quantity": quantity,
                    "included_boxes": included_boxes,
                    "plan_price": plan_price,
                }
            )

        unique_plan_tabs = {record["plan"].tab for record in plan_records}
        if len(unique_plan_tabs) > 1:
            raise ValueError("Please select one meal plan type per order.")

        primary_plan = plan_records[0]["plan"]
        plan_week_rules = getattr(primary_plan, "week_selection_rules", None)

        delivery_slot_models: List[DeliverySlotSelection] = []
        menu_totals: Dict[str, int] = defaultdict(int)
        unique_delivery_dates = set()

        for slot in delivery_slots:
            date_str = slot.get("delivery_date")
            menu_items = slot.get("menu_items", {})
            if not date_str or not menu_items:
                continue

            delivery_date = parse_date(date_str)
            delivery_slot_models.append(
                DeliverySlotSelection(
                    delivery_date=delivery_date,
                    menu_items=menu_items,
                    notes=slot.get("notes"),
                )
            )

            unique_delivery_dates.add(date_str)

            for item_id, quantity in menu_items.items():
                menu_totals[item_id] += int(quantity)

        if not delivery_slot_models:
            raise ValueError("No meals were selected for the delivery schedule")

        total_selected_boxes = sum(menu_totals.values())
        week_counts: Counter[str] = Counter()
        for slot in delivery_slot_models:
            delivery_date = slot.delivery_date
            week_start = delivery_date.date() - timedelta(days=delivery_date.weekday())
            week_counts[week_start.isoformat()] += 1

        if plan_week_rules and primary_plan.tab != "regular":
            required_weeks = (
                plan_week_rules.required_weeks
                or primary_plan.weeks_in_cycle
                or 1
            )
            available_weeks = plan_week_rules.available_weeks or max(
                required_weeks, len(week_counts)
            )
            deliveries_per_week_rule = (
                plan_week_rules.deliveries_per_week
                or primary_plan.deliveries_per_cycle
            )

            unique_week_count = len(week_counts)
            if unique_week_count < required_weeks:
                missing = required_weeks - unique_week_count
                raise ValueError(
                    f"{primary_plan.name} requires selections across "
                    f"{required_weeks} week(s). Choose {missing} more week"
                    f"{'' if missing == 1 else 's'} within the window."
                )

            if available_weeks and unique_week_count > available_weeks:
                raise ValueError(
                    f"{primary_plan.name} allows choosing from only "
                    f"{available_weeks} upcoming week(s)."
                )

            if (
                deliveries_per_week_rule
                and not plan_week_rules.allow_partial_weeks
            ):
                for week_key, count in week_counts.items():
                    if count != deliveries_per_week_rule:
                        raise ValueError(
                            f"Each selected week for {primary_plan.name} "
                            f"must include {deliveries_per_week_rule} delivery days."
                        )

        if has_subscription_plan and total_selected_boxes < total_included_boxes:
            missing = total_included_boxes - total_selected_boxes
            raise ValueError(f"Please select {missing} more meal(s) to complete your plan")

        if fulfilment == "delivery" and has_regular_plan and total_selected_boxes < REGULAR_DELIVERY_MIN_BOXES:
            raise ValueError(f"Regular delivery orders require at least {REGULAR_DELIVERY_MIN_BOXES} boxes")

        if fulfilment == "pickup" and has_regular_plan and total_selected_boxes < REGULAR_PICKUP_MIN_BOXES:
            raise ValueError(f"Regular pickup orders require at least {REGULAR_PICKUP_MIN_BOXES} box")

        if fulfilment == "pickup" and has_subscription_plan:
            raise ValueError("Meal subscription plans require delivery")

        remaining_included_boxes = total_included_boxes
        per_item_cap = max_boxes_per_meal_total if max_boxes_per_meal_total > 0 else None

        order_items: List[OrderItem] = []
        extra_boxes = 0
        extra_boxes_price = 0.0

        for item_id, quantity in menu_totals.items():
            menu_item = await menu_service.get_menu_item_by_id(item_id)
            if not menu_item or not menu_item.is_available:
                raise ValueError(f"Menu item {item_id} is no longer available")

            if has_subscription_plan and not menu_item.is_available_for_meal_plan:
                raise ValueError(f"{menu_item.name} is not available for meal subscriptions")

            allowed_for_item = quantity
            if per_item_cap is not None:
                allowed_for_item = min(quantity, per_item_cap)

            covered_quantity = min(allowed_for_item, remaining_included_boxes)
            if per_item_cap is None and total_included_boxes > 0:
                covered_quantity = min(quantity, remaining_included_boxes)

            extra_quantity = max(0, quantity - covered_quantity)
            remaining_included_boxes = max(0, remaining_included_boxes - covered_quantity)

            item_subtotal = menu_item.price * extra_quantity

            order_items.append(
                OrderItem(
                    item_id=str(menu_item.id),
                    item_name=menu_item.name,
                    category=menu_item.category,
                    quantity=quantity,
                    price=menu_item.price,
                    subtotal=item_subtotal
                )
            )

            extra_boxes += extra_quantity
            extra_boxes_price += item_subtotal

        subtotal = plan_base_total + extra_boxes_price

        delivery_days = len(unique_delivery_dates)
        delivery_fee = 0.0
        delivery_fee_per_day = 0.0

        if fulfilment == "delivery":
            address_required_fields = ["street", "suburb", "postcode"]
            if any(field not in address_data for field in address_required_fields):
                raise ValueError("Delivery address is incomplete")

            address_str = f"{address_data['street']}, {address_data['suburb']}, {address_data['postcode']}"
            delivery_fee, distance, geocoded = await delivery_service.calculate_weekly_delivery_fee(
                address_str,
                subtotal,
                max(delivery_days, 1),
                is_express
            )

            if geocoded:
                address_data["latitude"] = geocoded["latitude"]
                address_data["longitude"] = geocoded["longitude"]
                address_data["formatted_address"] = geocoded.get("formatted_address")

            delivery_fee_per_day = delivery_fee / max(delivery_days, 1)
        else:
            address_data = {"fulfilment": "pickup"}
            delivery_address_id = None

        total_amount = subtotal + delivery_fee

        plan_selection_models = []
        for record in plan_records:
            plan_obj = record["plan"]
            quantity = record["quantity"]
            weeks_in_cycle = plan_obj.weeks_in_cycle or (
                plan_obj.week_selection_rules.available_weeks
                if plan_obj.week_selection_rules and plan_obj.week_selection_rules.available_weeks
                else 0
            )
            selection = MealPlanSelection(
                plan_id=str(plan_obj.id),
                plan_code=plan_obj.code,
                plan_name=plan_obj.name,
                plan_tab=plan_obj.tab,
                quantity=quantity,
                included_meals=(plan_obj.included_meals or 0) * quantity,
                included_boxes=record["included_boxes"],
                deliveries_in_cycle=plan_obj.deliveries_per_cycle or delivery_days,
                weeks_in_cycle=weeks_in_cycle,
                max_boxes_per_meal=plan_obj.max_boxes_per_meal,
                available_delivery_days=plan_obj.available_delivery_days or [],
                week_selection_rules=plan_obj.week_selection_rules,
                customer_notifications=plan_obj.customer_notifications,
                metadata=plan_obj.metadata,
                plan_price=record["plan_price"],
                discount_applied=0.0,
            )
            plan_selection_models.append(selection)

        order_payload = {
            "items": [item.dict() for item in order_items],
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total_amount": total_amount,
            "delivery_method": (
                "pickup" if fulfilment == "pickup"
                else ("express" if is_express else "standard")
            ),
            "delivery_address": address_data,
            "delivery_address_id": delivery_address_id,
            "delivery_instructions": delivery_instructions,
            "notes": notes,
            "payment_method": (payment_method or "cash").lower(),
        }

        subscription_payload = {
            "user_id": ObjectId(user_id),
            "fulfilment_type": fulfilment,
            "postal_code": address_data.get("postcode") if fulfilment == "delivery" else None,
            "plan_selections": [selection.dict() for selection in plan_selection_models],
            "delivery_slots": [slot.dict() for slot in delivery_slot_models],
            "total_selected_boxes": total_selected_boxes,
            "total_included_boxes": total_included_boxes,
            "extra_boxes": extra_boxes,
            "extra_boxes_price": extra_boxes_price,
            "delivery_days": delivery_days,
            "delivery_fee_per_day": delivery_fee_per_day,
            "total_delivery_fee": delivery_fee,
            "express_delivery": fulfilment == "delivery" and is_express,
            "delivery_fee_notes": None,
            "reminder_settings": (
                primary_plan.reminder_settings.dict()
                if getattr(primary_plan, "reminder_settings", None)
                else None
            ),
            "reminders_sent": [],
            "is_active": True,
        }

        remaining_unfilled = max(total_included_boxes - total_selected_boxes, 0)
        return order_payload, subscription_payload, plan_records, remaining_unfilled

    async def create_meal_subscription_order(
        self,
        user_id: str,
        plan_selections: List[Dict],
        delivery_slots: List[Dict],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
        delivery_address_id: Optional[str] = None,
    ) -> tuple[OrderModel, MealSubscriptionModel]:
        """Create a configurable meal subscription (weekly/fortnight/monthly/regular) order."""
        try:
            if self.orders is None or self.db is None:
                raise ValueError("Database not connected")

            subscription_collection = (
                self.meal_subs
                if self.meal_subs is not None
                else self.weekly_subs_legacy
            )
            if subscription_collection is None:
                raise ValueError("Meal subscription collection not available")

            (
                order_payload,
                subscription_payload,
                plan_records,
                remaining_unfilled,
            ) = await self._prepare_meal_subscription_documents(
                user_id,
                plan_selections,
                delivery_slots,
                delivery_address,
                fulfilment_method,
                is_express,
                delivery_instructions,
                notes,
                payment_method,
                delivery_address_id,
            )

            now = datetime.utcnow()
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),
                "order_type": OrderType.MEAL_SUBSCRIPTION,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "created_at": now,
                "updated_at": now,
                **order_payload,
            }

            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id

            subscription_dict = {
                **subscription_payload,
                "order_id": result.inserted_id,
                "user_id": ObjectId(user_id),
                "created_at": now,
                "updated_at": now,
            }

            sub_result = await subscription_collection.insert_one(subscription_dict)
            subscription_dict["_id"] = sub_result.inserted_id

            await reminder_service.schedule_reminders_for_subscription(
                subscription_dict["_id"],
                plan_records,
                remaining_unfilled,
            )

            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "subtotal": order_dict["subtotal"],
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "delivery_instructions": order_dict["delivery_instructions"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"],
            }

            logger.info("Meal subscription order created: %s", order_dict["order_number"])
            return OrderModel(**response_dict), MealSubscriptionModel(**subscription_dict)

        except Exception as e:
            logger.error(f"Error creating meal subscription order: {e}")
            raise

    async def update_meal_subscription_order(
        self,
        order_id: str,
        user_id: str,
        plan_selections: List[Dict],
        delivery_slots: List[Dict],
        delivery_address: Optional[dict],
        fulfilment_method: str,
        is_express: bool,
        delivery_instructions: str = None,
        notes: str = None,
        payment_method: str = "cash",
        delivery_address_id: Optional[str] = None,
    ) -> OrderModel:
        """Update an existing meal subscription order."""
        if self.orders is None or self.db is None:
            raise ValueError("Database not connected")

        subscription_collection = (
            self.meal_subs if self.meal_subs is not None else self.weekly_subs_legacy
        )
        if subscription_collection is None:
            raise ValueError("Meal subscription collection not available")

        order_filter = {
            "_id": ObjectId(order_id),
            "user_id": ObjectId(user_id),
        }
        existing_order = await self.orders.find_one(order_filter)
        if not existing_order:
            raise ValueError("Order not found")

        if existing_order.get("order_type") != OrderType.MEAL_SUBSCRIPTION:
            raise ValueError("Only meal subscription orders can be edited")

        if existing_order.get("status") in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
            raise ValueError("This order can no longer be edited")

        (
            order_payload,
            subscription_payload,
            plan_records,
            remaining_unfilled,
        ) = await self._prepare_meal_subscription_documents(
            user_id,
            plan_selections,
            delivery_slots,
            delivery_address,
            fulfilment_method,
            is_express,
            delivery_instructions,
            notes,
            payment_method,
            delivery_address_id,
        )

        now = datetime.utcnow()
        await self.orders.update_one(
            order_filter,
            {
                "$set": {
                    **order_payload,
                    "updated_at": now,
                }
            },
        )

        subscription_filter = {"order_id": ObjectId(order_id)}
        existing_subscription = await subscription_collection.find_one(subscription_filter)
        subscription_dict = {
            **subscription_payload,
            "order_id": ObjectId(order_id),
            "user_id": ObjectId(user_id),
            "created_at": existing_subscription.get("created_at") if existing_subscription else now,
            "updated_at": now,
        }

        if existing_subscription:
            await subscription_collection.update_one(
                subscription_filter,
                {"$set": subscription_dict},
            )
            subscription_id = existing_subscription["_id"]
        else:
            insert_result = await subscription_collection.insert_one(subscription_dict)
            subscription_id = insert_result.inserted_id

        await reminder_service.schedule_reminders_for_subscription(
            subscription_id,
            plan_records,
            remaining_unfilled,
        )

        updated = await self.get_order_by_id(order_id)
        if not updated:
            raise ValueError("Failed to load updated order")
        return updated

    async def get_meal_subscription_details(
        self,
        order_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return subscription-specific metadata for a meal subscription order."""
        if self.orders is None:
            return None

        order = await self.orders.find_one(
            {"_id": ObjectId(order_id), "user_id": ObjectId(user_id)}
        )
        if not order:
            return None

        if order.get("order_type") != OrderType.MEAL_SUBSCRIPTION:
            raise ValueError("Only meal subscription orders contain schedule data")

        subscription_collection = (
            self.meal_subs if self.meal_subs is not None else self.weekly_subs_legacy
        )
        if subscription_collection is None:
            return None

        subscription = await subscription_collection.find_one(
            {"order_id": ObjectId(order_id)}
        )
        if not subscription:
            return None

        plan_selections = []
        for selection in subscription.get("plan_selections", []):
            plan_selections.append(
                {
                    "plan_id": selection.get("plan_id"),
                    "plan_code": selection.get("plan_code"),
                    "plan_name": selection.get("plan_name"),
                    "quantity": selection.get("quantity", 1),
                }
            )

        delivery_slots = []
        for slot in subscription.get("delivery_slots", []):
            date_val = slot.get("delivery_date")
            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val)
            delivery_slots.append(
                {
                    "delivery_date": date_str,
                    "menu_items": slot.get("menu_items", {}),
                }
            )

        return {
            "order_id": str(order["_id"]),
            "order_number": order.get("order_number"),
            "plan_selections": plan_selections,
            "delivery_slots": delivery_slots,
            "fulfilment_method": subscription.get(
                "fulfilment_type", order.get("delivery_method")
            ),
            "is_express": bool(subscription.get("express_delivery")),
            "delivery_address_id": order.get("delivery_address_id"),
            "delivery_instructions": order.get("delivery_instructions"),
            "notes": order.get("notes"),
            "payment_method": order.get("payment_method"),
        }

    async def create_catering_order(
        self,
        user_id: str,
        package_type: str,
        guest_count: int,
        event_date: str,
        event_time: str,
        venue_address: str,
        selected_items: Dict[str, List[str]],
        special_requests: str = None,
        payment_method: str = "cash"
    ) -> tuple[OrderModel, CateringOrderModel]:
        """Create catering order"""
        try:
            if self.orders is None or self.catering_orders is None:
                raise ValueError("Database not connected")
                
            # Get package pricing
            price_per_head = {
                "basic": CATERING_BASIC_PRICE,
                "premium": CATERING_PREMIUM_PRICE,
                "diamond": CATERING_DIAMOND_PRICE
            }[package_type]
            
            package_total = price_per_head * guest_count
            
            # Calculate delivery fee (simplified)
            delivery_fee = CATERING_BASE_DELIVERY_FEE
            
            total_amount = package_total + delivery_fee
            advance_payment = total_amount * CATERING_ADVANCE_PAYMENT_PERCENT
            remaining_payment = total_amount - advance_payment
            
            # Build order items from selected items
            order_items = []
            for category, item_ids in selected_items.items():
                for item_id in item_ids:
                    menu_item = await menu_service.get_menu_item_by_id(item_id)
                    if not menu_item:
                        raise ValueError(f"Item {item_id} not found")
                    
                    order_item = OrderItem(
                        item_id=str(menu_item.id),
                        item_name=menu_item.name,
                        category=category,
                        quantity=guest_count,
                        price=price_per_head,
                        subtotal=package_total
                    )
                    order_items.append(order_item)
            
            # Create order document
            order_dict = {
                "order_number": generate_order_number(),
                "user_id": ObjectId(user_id),
                "order_type": OrderType.CATERING,
                "status": OrderStatus.PENDING,
                "payment_status": PaymentStatus.PENDING,
                "payment_method": (payment_method or "cash").lower(),
                "items": [item.dict() for item in order_items],
                "subtotal": package_total,
                "delivery_fee": delivery_fee,
                "total_amount": total_amount,
                "delivery_method": "standard",
                "delivery_address": {"street": venue_address},
                "notes": special_requests,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.orders.insert_one(order_dict)
            order_dict["_id"] = result.inserted_id
            
            # Create catering record
            event_date_parsed = parse_date(event_date)
            
            catering_dict = {
                "order_id": result.inserted_id,
                "user_id": ObjectId(user_id),
                "event_date": event_date_parsed,
                "event_time": event_time,
                "venue_address": venue_address,
                "guest_count": guest_count,
                "package_type": package_type,
                "package_price_per_head": price_per_head,
                "selected_items": selected_items,
                "package_total": package_total,
                "delivery_fee": delivery_fee,
                "advance_payment_amount": advance_payment,
                "remaining_payment_amount": remaining_payment,
                "advance_paid": False,
                "final_paid": False,
                "quote_sent": False,
                "quote_accepted": False,
                "special_requests": special_requests,
                "created_at": datetime.utcnow()
            }
            
            cat_result = await self.catering_orders.insert_one(catering_dict)
            catering_dict["_id"] = cat_result.inserted_id
            
            # Convert ObjectIds to strings for response
            response_dict = {
                "_id": str(order_dict["_id"]),
                "order_number": order_dict["order_number"],
                "user_id": str(order_dict["user_id"]),
                "order_type": order_dict["order_type"],
                "status": order_dict["status"],
                "payment_status": order_dict["payment_status"],
                "items": order_dict["items"],
                "subtotal": order_dict["subtotal"],
                "delivery_fee": order_dict["delivery_fee"],
                "total_amount": order_dict["total_amount"],
                "delivery_method": order_dict["delivery_method"],
                "delivery_address": order_dict["delivery_address"],
                "notes": order_dict["notes"],
                "payment_method": order_dict["payment_method"],
                "created_at": order_dict["created_at"],
                "updated_at": order_dict["updated_at"]
            }
            
            logger.info(f"Catering order created: {order_dict['order_number']}")
            return OrderModel(**response_dict), CateringOrderModel(**catering_dict)
            
        except Exception as e:
            logger.error(f"Error creating catering order: {e}")
            raise
    
    async def get_order_by_id(self, order_id: str) -> Optional[OrderModel]:
        """Get order by ID"""
        try:
            if self.orders is None:
                return None
                
            order = await self.orders.find_one({"_id": ObjectId(order_id)})
            if order:
                # Convert ObjectIds to strings
                order["_id"] = str(order["_id"])
                order["user_id"] = str(order["user_id"])
                return OrderModel(**order)
            return None
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None
    
    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20) -> List[OrderModel]:
        """Get user's orders"""
        try:
            if self.orders is None:
                return []
                
            cursor = self.orders.find(
                {"user_id": ObjectId(user_id)}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            orders = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings
            result = []
            for order in orders:
                order["_id"] = str(order["_id"])
                order["user_id"] = str(order["user_id"])
                result.append(OrderModel(**order))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    async def update_order_status(self, order_id: str, status: str, admin_notes: str = None) -> OrderModel:
        """Update order status"""
        try:
            if self.orders is None:
                raise ValueError("Database not connected")
                
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if admin_notes:
                update_data["admin_notes"] = admin_notes
            
            if status == OrderStatus.DELIVERED:
                update_data["delivered_at"] = datetime.utcnow()
            
            await self.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            
            order = await self.get_order_by_id(order_id)
            logger.info(f"Order status updated: {order_id} -> {status}")
            return order
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            raise
    
    async def update_payment_status(self, order_id: str, payment_status: str, payment_intent_id: str = None) -> OrderModel:
        """Update payment status"""
        try:
            if self.orders is None:
                raise ValueError("Database not connected")
                
            update_data = {
                "payment_status": payment_status,
                "updated_at": datetime.utcnow()
            }
            
            if payment_intent_id:
                update_data["stripe_payment_intent_id"] = payment_intent_id
            
            if payment_status == PaymentStatus.PAID:
                # Get the order first to get total amount
                order = await self.get_order_by_id(order_id)
                if order:
                    update_data["paid_amount"] = order.total_amount
                update_data["status"] = OrderStatus.CONFIRMED
            
            await self.orders.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            
            order = await self.get_order_by_id(order_id)
            logger.info(f"Payment status updated: {order_id} -> {payment_status}")
            return order
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            raise

order_service = OrderService()




```

---

#### 📄 payment_service.py
**Path:** `app\services\payment_service.py`

```python
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
```

---

#### 📄 reminder_service.py
**Path:** `app\services\reminder_service.py`

```python
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.config.database import get_database
from app.services.notification_service import notification_service
from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self):
        self._db = None
        self._subscriptions = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def subscriptions(self):
        if self._subscriptions is None and self.db is not None:
            self._subscriptions = self.db.meal_subscriptions
        return self._subscriptions

    @staticmethod
    def _resolve_plan_settings(plan_records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for record in plan_records:
            plan = record.get("plan")
            if not plan:
                continue
            settings = getattr(plan, "reminder_settings", None) or record.get("reminder_settings")
            enabled = getattr(settings, "enabled", False)
            if isinstance(settings, dict):
                enabled = settings.get("enabled", False)
            if not enabled:
                continue
            if hasattr(settings, "model_dump"):
                return settings.model_dump()
            return dict(settings)
        return None

    async def schedule_reminders_for_subscription(
        self,
        subscription_id: ObjectId,
        plan_records: List[Dict[str, Any]],
        remaining_boxes: int,
    ) -> None:
        if self.subscriptions is None:
            return

        settings = self._resolve_plan_settings(plan_records)
        if not settings or not settings.get("enabled"):
            return

        threshold = settings.get("threshold_unselected_boxes") or 0
        if remaining_boxes <= threshold:
            return

        frequency_days = max(int(settings.get("frequency_days", 7)), 1)
        next_reminder_at = datetime.utcnow() + timedelta(days=frequency_days)

        await self.subscriptions.update_one(
            {"_id": subscription_id},
            {
                "$set": {
                    "reminder_settings": settings,
                    "next_reminder_at": next_reminder_at,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    async def process_due_reminders(self) -> int:
        if self.subscriptions is None:
            return 0

        now = datetime.utcnow()
        cursor = self.subscriptions.find(
            {
                "is_active": True,
                "next_reminder_at": {"$lte": now},
                "reminder_settings.enabled": True,
            }
        ).limit(100)

        due_subscriptions = await cursor.to_list(length=100)
        processed = 0

        for subscription in due_subscriptions:
            try:
                total_included = subscription.get("total_included_boxes", 0)
                total_selected = subscription.get("total_selected_boxes", 0)
                remaining = max(total_included - total_selected, 0)

                settings = subscription.get("reminder_settings") or {}
                threshold = settings.get("threshold_unselected_boxes") or 0

                if remaining <= threshold:
                    await self.subscriptions.update_one(
                        {"_id": subscription["_id"]},
                        {"$set": {"next_reminder_at": None}},
                    )
                    continue

                sent = await self._send_reminder(subscription, remaining)
                if not sent:
                    continue

                frequency_days = max(int(settings.get("frequency_days", 7)), 1)
                next_time = now + timedelta(days=frequency_days)

                await self.subscriptions.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "next_reminder_at": next_time,
                            "updated_at": datetime.utcnow(),
                        },
                        "$push": {"reminders_sent": now.isoformat()},
                    },
                )
                processed += 1
            except Exception as exc:
                logger.error("Failed to process reminder: %s", exc, exc_info=True)

        return processed

    async def _send_reminder(self, subscription: Dict[str, Any], remaining: int) -> bool:
        try:
            user = await auth_service.get_user_by_id(str(subscription["user_id"]))
            if not user or not user.get("phone"):
                logger.warning("Skipping reminder; user or phone missing.")
                return False

            plan_names = [selection.get("plan_code") for selection in subscription.get("plan_selections", [])]
            plan_summary = ", ".join(filter(None, plan_names)) or "your meal plan"

            message = (
                f"Hi {user.get('first_name') or ' there'}, you still have {remaining} box(es) to assign for {plan_summary}. "
                "Jump back in to finish your selections before the weekly cut-off."
            )

            return await notification_service.send_whatsapp_message(user["phone"], message)
        except Exception as exc:
            logger.error("Failed to send reminder notification: %s", exc, exc_info=True)
            return False


reminder_service = ReminderService()
```

---

#### 📄 subscription_service.py
**Path:** `app\services\subscription_service.py`

```python
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from bson import ObjectId

from app.config.database import get_database
from app.models.subscription import MealSubscriptionPlanModel
from app.models.menu import MenuItemModel
from app.services.menu_service import menu_service
from app.schemas.subscription import VALID_DELIVERY_DAYS
from app.utils.constants import LEGACY_DEFAULT_PLAN_CODES
import logging

logger = logging.getLogger(__name__)


class MealSubscriptionService:
    """Service layer for managing meal subscription plans and metadata."""

    def __init__(self):
        self._db = None
        self._plans_collection = None
        self._subscriptions_collection = None

    async def purge_legacy_defaults(self) -> int:
        """Remove any legacy default plans by code."""
        if self.plans is None or not LEGACY_DEFAULT_PLAN_CODES:
            return 0
        result = await self.plans.delete_many({"code": {"$in": LEGACY_DEFAULT_PLAN_CODES}})
        return result.deleted_count or 0

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def plans(self):
        if self._plans_collection is None and self.db is not None:
            self._plans_collection = self.db.meal_subscription_plans
        return self._plans_collection

    @property
    def subscriptions(self):
        if self._subscriptions_collection is None and self.db is not None:
            self._subscriptions_collection = self.db.meal_subscriptions
        return self._subscriptions_collection

    def _normalize_plan_doc(self, doc: Dict[str, Any]) -> None:
        """Ensure delivery day metadata and menu mappings are normalized."""
        raw_days = doc.get("available_delivery_days") or []
        normalized_days: List[str] = []
        for day in raw_days:
            if day is None:
                continue
            normalized = str(day).strip().lower()
            if normalized in VALID_DELIVERY_DAYS and normalized not in normalized_days:
                normalized_days.append(normalized)
        doc["available_delivery_days"] = normalized_days

        raw_mapping = doc.get("menu_item_ids_by_day") or {}
        normalized_mapping: Dict[str, List[str]] = {}
        for raw_day, item_ids in raw_mapping.items():
            if raw_day is None:
                continue
            day = str(raw_day).strip().lower()
            if day not in VALID_DELIVERY_DAYS:
                continue
            if not isinstance(item_ids, list):
                continue
            normalized_ids: List[str] = []
            for item_id in item_ids:
                if item_id is None:
                    continue
                if isinstance(item_id, ObjectId):
                    normalized_ids.append(str(item_id))
                else:
                    normalized_ids.append(str(item_id))
            normalized_mapping[day] = normalized_ids
        doc["menu_item_ids_by_day"] = normalized_mapping

        if not doc["available_delivery_days"] and normalized_mapping:
            doc["available_delivery_days"] = list(normalized_mapping.keys())

        terms = doc.get("terms_and_conditions")
        if isinstance(terms, list):
            doc["terms_and_conditions"] = [
                str(term).strip() for term in terms if str(term).strip()
            ]
        elif terms:
            doc["terms_and_conditions"] = [str(terms).strip()]
        else:
            doc["terms_and_conditions"] = []

        # Normalize metadata
        metadata = doc.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        menu_scope = metadata.get("menu_item_scope") or "meal_plan_only"
        menu_scope = (
            menu_scope.strip().lower()
            if isinstance(menu_scope, str)
            else "meal_plan_only"
        )
        if menu_scope not in {"meal_plan_only", "all_menu_items"}:
            menu_scope = "meal_plan_only"
        metadata["menu_item_scope"] = menu_scope
        doc["metadata"] = metadata

        # Normalize notification settings
        notifications = doc.get("customer_notifications") or {}
        upsell_condition = notifications.get("upsell_condition") or "always"
        if not isinstance(upsell_condition, str):
            upsell_condition = "always"
        upsell_condition = upsell_condition.strip().lower()
        if upsell_condition not in {
            "always",
            "when_plan_selected",
            "when_no_plan",
            "hidden",
        }:
            upsell_condition = "always"
        notifications["upsell_condition"] = upsell_condition
        doc["customer_notifications"] = notifications

        # Normalize reminder settings
        reminder_settings = doc.get("reminder_settings")
        if reminder_settings:
            normalized_reminder = {
                "enabled": bool(reminder_settings.get("enabled", False)),
                "frequency_days": int(
                    reminder_settings.get("frequency_days", 7) or 7
                ),
                "channel": (
                    str(reminder_settings.get("channel", "in_app")).strip().lower()
                    or "in_app"
                ),
                "threshold_unselected_boxes": reminder_settings.get(
                    "threshold_unselected_boxes"
                ),
            }
            if normalized_reminder["frequency_days"] < 1:
                normalized_reminder["frequency_days"] = 1
            if normalized_reminder["frequency_days"] > 30:
                normalized_reminder["frequency_days"] = 30
            if normalized_reminder["channel"] not in {"in_app", "email", "both"}:
                normalized_reminder["channel"] = "in_app"
            threshold = normalized_reminder["threshold_unselected_boxes"]
            if threshold is not None:
                try:
                    threshold_value = int(threshold)
                    normalized_reminder["threshold_unselected_boxes"] = max(
                        threshold_value, 0
                    )
                except (ValueError, TypeError):
                    normalized_reminder["threshold_unselected_boxes"] = None
            doc["reminder_settings"] = normalized_reminder
        else:
            doc["reminder_settings"] = None

        # Ensure is_active defaults to True if missing
        if "is_active" not in doc or doc["is_active"] is None:
            doc["is_active"] = True

    def _menu_item_to_response_dict(self, item: MenuItemModel) -> Dict[str, Any]:
        """Convert a menu item model into the response structure expected by clients."""
        created_at = (
            item.created_at.isoformat()
            if isinstance(item.created_at, datetime)
            else str(item.created_at)
        )
        updated_at = (
            item.updated_at.isoformat()
            if isinstance(item.updated_at, datetime)
            else str(item.updated_at)
        )

        return {
            "id": str(item.id),
            "_id": str(item.id),
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "price": item.price,
            "image_url": getattr(item, "image_url", None),
            "is_available": getattr(item, "is_available", True),
            "is_available_for_daily": getattr(item, "is_available_for_daily", False),
            "is_available_for_meal_plan": getattr(item, "is_available_for_meal_plan", False),
            "allergens": item.allergens or [],
            "spice_level": item.spice_level,
            "is_vegetarian": getattr(item, "is_vegetarian", False),
            "is_vegan": getattr(item, "is_vegan", False),
            "is_halal": getattr(item, "is_halal", True),
            "nutritional_info": getattr(item, "nutritional_info", None),
            "serving_size": getattr(item, "serving_size", None),
            "created_at": created_at,
            "updated_at": updated_at,
        }

    async def _attach_menu_items(self, plan_docs: List[Dict[str, Any]]) -> None:
        """Attach detailed menu information to each plan document."""
        unique_ids: Dict[str, None] = {}
        for doc in plan_docs:
            mapping = doc.get("menu_item_ids_by_day") or {}
            for item_ids in mapping.values():
                for item_id in item_ids or []:
                    unique_ids[str(item_id)] = None

        if not unique_ids:
            for doc in plan_docs:
                doc.setdefault("menu_items_by_day", {})
            return

        menu_items = await menu_service.get_menu_items_by_ids(list(unique_ids.keys()))
        lookup: Dict[str, Dict[str, Any]] = {}
        for item in menu_items:
            if not item or item.id is None:
                continue
            lookup[str(item.id)] = self._menu_item_to_response_dict(item)

        for doc in plan_docs:
            mapping = doc.get("menu_item_ids_by_day") or {}
            enriched: Dict[str, List[Dict[str, Any]]] = {}
            for day, item_ids in mapping.items():
                if not isinstance(item_ids, list):
                    continue
                enriched[day] = [
                    lookup[item_id] for item_id in item_ids if item_id in lookup
                ]
            doc["menu_items_by_day"] = enriched

    async def list_plans(
        self,
        tab: Optional[str] = None,
        include_inactive: bool = False,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[MealSubscriptionPlanModel], int]:
        """Return plans filtered by tab and activity with pagination support."""
        if self.plans is None:
            return [], 0

        query: Dict[str, Any] = {}
        if tab:
            query["tab"] = tab
        if not include_inactive:
            query["$or"] = [
                {"is_active": True},
                {"is_active": {"$exists": False}},
            ]

        skip = max(0, (page - 1) * page_size)
        total = await self.plans.count_documents(query)

        cursor = (
            self.plans.find(query)
            .sort("display_order", 1)
            .skip(skip)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)

        for doc in results:
            self._normalize_plan_doc(doc)

        await self._attach_menu_items(results)

        plans: List[MealSubscriptionPlanModel] = []
        for doc in results:
            doc["_id"] = str(doc["_id"])
            plans.append(MealSubscriptionPlanModel(**doc))
        return plans, total

    async def get_plan_by_id(self, plan_id: str) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return None

        doc = await self.plans.find_one({"_id": ObjectId(plan_id)})
        if not doc:
            return None
        self._normalize_plan_doc(doc)
        await self._attach_menu_items([doc])
        doc["_id"] = str(doc["_id"])
        return MealSubscriptionPlanModel(**doc)

    async def get_plan_by_code(self, code: str) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None:
            return None

        doc = await self.plans.find_one({"code": code})
        if not doc:
            return None
        self._normalize_plan_doc(doc)
        await self._attach_menu_items([doc])
        doc["_id"] = str(doc["_id"])
        return MealSubscriptionPlanModel(**doc)

    async def create_plan(self, plan_data: Dict[str, Any]) -> MealSubscriptionPlanModel:
        if self.plans is None:
            raise ValueError("Meal subscription plans collection not available")

        now = datetime.utcnow()

        normalized_code = plan_data.get("code")
        if normalized_code:
            normalized_code = normalized_code.strip().lower().replace(" ", "_")

        # Prevent duplicate codes
        if normalized_code:
            existing = await self.plans.find_one({"code": normalized_code})
            if existing:
                raise ValueError(f"Plan code '{normalized_code}' already exists")

        plan_doc = {
            **plan_data,
            "created_at": now,
            "updated_at": now,
        }
        if normalized_code:
            plan_doc["code"] = normalized_code

        self._normalize_plan_doc(plan_doc)
        result = await self.plans.insert_one(plan_doc)
        plan_doc["_id"] = str(result.inserted_id)
        await self._attach_menu_items([plan_doc])
        logger.info("Meal subscription plan created: %s", plan_doc["code"])
        return MealSubscriptionPlanModel(**plan_doc)

    async def update_plan(self, plan_id: str, update_data: Dict[str, Any]) -> Optional[MealSubscriptionPlanModel]:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return None

        update_payload = {k: v for k, v in update_data.items() if v is not None}
        if not update_payload:
            return await self.get_plan_by_id(plan_id)

        if "code" in update_payload and update_payload["code"]:
            normalized_code = (
                update_payload["code"].strip().lower().replace(" ", "_")
            )
            update_payload["code"] = normalized_code

            if self.plans is not None:
                existing = await self.plans.find_one(
                    {"code": normalized_code, "_id": {"$ne": ObjectId(plan_id)}}
                )
                if existing:
                    raise ValueError(f"Plan code '{normalized_code}' already exists")

        if (
            "available_delivery_days" in update_payload
            or "menu_item_ids_by_day" in update_payload
        ):
            temp_doc = {
                "available_delivery_days": update_payload.get(
                    "available_delivery_days", []
                ),
                "menu_item_ids_by_day": update_payload.get(
                    "menu_item_ids_by_day", {}
                ),
            }
            self._normalize_plan_doc(temp_doc)
            if "available_delivery_days" in update_payload:
                update_payload["available_delivery_days"] = temp_doc[
                    "available_delivery_days"
                ]
            if "menu_item_ids_by_day" in update_payload:
                update_payload["menu_item_ids_by_day"] = temp_doc[
                    "menu_item_ids_by_day"
                ]

        if "terms_and_conditions" in update_payload:
            terms = update_payload.get("terms_and_conditions") or []
            update_payload["terms_and_conditions"] = [
                str(term).strip() for term in terms if str(term).strip()
            ]

        # Prevent immutable fields from being updated
        update_payload.pop("_id", None)
        update_payload.pop("id", None)

        update_payload["updated_at"] = datetime.utcnow()

        result = await self.plans.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": update_payload}
        )
        if result.matched_count == 0:
            return None
        return await self.get_plan_by_id(plan_id)

    async def delete_plan(self, plan_id: str) -> bool:
        if self.plans is None or not ObjectId.is_valid(plan_id):
            return False

        result = await self.plans.delete_one({"_id": ObjectId(plan_id)})
        return result.deleted_count > 0


meal_subscription_service = MealSubscriptionService()
```

---

### 📁 app\utils

#### 📄 __init__.py
**Path:** `app\utils\__init__.py`

```python

```

---

#### 📄 constants.py
**Path:** `app\utils\constants.py`

```python
from enum import Enum

class OrderType(str, Enum):
    DAILY = "daily"
    MEAL_SUBSCRIPTION = "meal_subscription"
    CATERING = "catering"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_PAID = "partially_paid"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class FoodCategory(str, Enum):
    RICE = "rice"
    CURRY = "curry"
    BBQ = "bbq"
    SWEETS = "sweets"
    DRINKS = "drinks"

class CateringPackage(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    DIAMOND = "diamond"

class DeliveryMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    PICKUP = "pickup"

# Daily Menu Delivery Defaults
DAILY_DELIVERY_FEE = 10.0
DAILY_DELIVERY_RADIUS = 6.0  # km from Guildford

# Meal Subscription Tabs
MEAL_PLAN_TAB_REGULAR = "regular"
MEAL_PLAN_TAB_WEEKLY = "weekly"
MEAL_PLAN_TAB_FORTNIGHT = "fortnight"
MEAL_PLAN_TAB_MONTHLY = "monthly"

# Meal Subscription Defaults
REGULAR_DELIVERY_MIN_BOXES = 4
REGULAR_PICKUP_MIN_BOXES = 1
DEFAULT_MEAL_PLAN_MAX_BOXES_PER_MEAL = 2
DEFAULT_EXTRA_BOX_PRICE = 12.0
DEFAULT_EXPRESS_FEE_PER_DAY = 10.0

LEGACY_DEFAULT_PLAN_CODES = [
    "regular_flex",
    "weekly_10_meal",
    "fortnight_duo",
    "monthly_builder",
]

# Catering Constants
CATERING_BASIC_PRICE = 25.0
CATERING_PREMIUM_PRICE = 35.0
CATERING_DIAMOND_PRICE = 50.0
CATERING_ADVANCE_PAYMENT_PERCENT = 0.5
CATERING_BASE_DELIVERY_FEE = 30.0

# Order Number Format
ORDER_NUMBER_PREFIX = "BF"
```

---

#### 📄 default_delivery_zones.py
**Path:** `app\utils\default_delivery_zones.py`

```python
"""
Default delivery zones covering meal subscription service areas.

These records are used to seed the MongoDB `delivery_zones` collection when
it is empty. They intentionally focus on meal subscription coverage – the
daily menu retains its 6 km delivery radius and does not rely on this table.
"""
from __future__ import annotations

from typing import List, Dict

MEAL_SUBSCRIPTION_NOTE = "Meal subscriptions only"


def _zone(
    zone_label: str,
    postcode: str,
    suburbs: List[str],
    base_delivery_fee: float,
    max_distance_km: float,
    notes: str | None = None,
) -> Dict[str, object]:
    """Helper to create a consistent delivery zone payload."""
    payload: Dict[str, object] = {
        "zone_label": zone_label,
        "postcode": postcode,
        "suburbs": suburbs,
        "base_delivery_fee": base_delivery_fee,
        "distance_from_business": max_distance_km,
        "order_types": ["meal_subscription"],
        "is_active": True,
        "notes": notes or MEAL_SUBSCRIPTION_NOTE,
    }
    return payload


ZONE_1_FEE = 10.0
ZONE_2_FEE = 14.0
ZONE_3_FEE = 20.0

ZONE_1_DISTANCE = 14.0
ZONE_2_DISTANCE = 20.0
ZONE_3_DISTANCE = 30.0

DEFAULT_MEAL_DELIVERY_ZONES: List[Dict[str, object]] = [
    # Zone 1 (0-14 km)
    _zone("Zone 1 (0-14 km)", "2161", ["Guildford", "Guildford West", "Yennora", "Old Guildford"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2160", ["Merrylands", "Merrylands West"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2142", ["Granville", "South Granville", "Holroyd", "Rosehill", "Clyde"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2150", ["Parramatta", "Harris Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2145", ["Mays Hill", "Westmead", "South Wentworthville"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2165", ["Fairfield", "Fairfield East", "Fairfield Heights"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2162", ["Chester Hill", "Sefton"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2163", ["Villawood", "Carramar", "Lansdowne"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2141", ["Berala"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2143", ["Regents Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2144", ["Auburn"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2146", ["Toongabbie", "Old Toongabbie"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2147", ["Seven Hills"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2148", ["Smithfield", "Smithfield West", "Woodpark", "Wetherill Park"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2151", ["North Parramatta"], ZONE_1_FEE, ZONE_1_DISTANCE),
    _zone("Zone 1 (0-14 km)", "2152", ["Northmead"], ZONE_1_FEE, ZONE_1_DISTANCE),

    # Zone 2 (14-20 km)
    _zone("Zone 2 (14-20 km)", "2166", ["Cabramatta", "Cabramatta West", "Canley Vale", "Lansvale", "Canley Heights"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2168", ["Ashcroft", "Busby", "Cartwright", "Miller", "Heckenberg", "Sadlier"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2170", ["Liverpool", "Mount Pritchard", "Warwick Farm", "Lurnea", "Casula (north)"], ZONE_2_FEE, ZONE_2_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – northern catchment"),
    _zone("Zone 2 (14-20 km)", "2171", ["Hoxton Park", "Hinchinbrook", "Middleton Grange (north)", "Green Valley"], ZONE_2_FEE, ZONE_2_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – northern catchment"),
    _zone("Zone 2 (14-20 km)", "2153", ["Baulkham Hills", "Bella Vista", "Winston Hills"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2154", ["Castle Hill (southern side)", "Norwest"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2129", ["Homebush Bay"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2127", ["Sydney Olympic Park"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2126", ["Cherrybrook (southern side)"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2117", ["Dundas", "Telopea"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2122", ["Eastwood"], ZONE_2_FEE, ZONE_2_DISTANCE),
    _zone("Zone 2 (14-20 km)", "2118", ["Carlingford"], ZONE_2_FEE, ZONE_2_DISTANCE),

    # Zone 3 (20-30 km)
    _zone("Zone 3 (20-30 km)", "2170", ["Casula (south)", "Moorebank", "Chipping Norton", "Prestons"], ZONE_3_FEE, ZONE_3_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – southern catchment"),
    _zone("Zone 3 (20-30 km)", "2171", ["Middleton Grange (south)", "West Hoxton", "Carnes Hill"], ZONE_3_FEE, ZONE_3_DISTANCE, f"{MEAL_SUBSCRIPTION_NOTE} – southern catchment"),
    _zone("Zone 3 (20-30 km)", "2172", ["Sandy Point", "Voyager Point", "Pleasure Point"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2763", ["Quakers Hill"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2761", ["Glendenning", "Oakhurst"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2770", ["Rooty Hill", "Minchinbury"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2155", ["Kellyville", "Kellyville Ridge", "Beaumont Hills"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2156", ["Glenhaven", "Annangrove"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2157", ["Glenorie", "Canoelands", "Forest Glen"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2158", ["Dural", "Middle Dural", "Round Corner"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2159", ["Galston", "Arcadia", "Berrilee"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2765", ["Marsden Park", "Riverstone"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2565", ["Leppington (north)"], ZONE_3_FEE, ZONE_3_DISTANCE),
    _zone("Zone 3 (20-30 km)", "2167", ["Glenfield (south)"], ZONE_3_FEE, ZONE_3_DISTANCE),
]
```

---

#### 📄 helpers.py
**Path:** `app\utils\helpers.py`

```python
from datetime import datetime
import random
import string
from app.utils.constants import ORDER_NUMBER_PREFIX

def generate_order_number() -> str:
    """
    Generate unique order number in format: BF-YYYYMMDD-RANDOM6
    
    Returns:
        Unique order number string
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{ORDER_NUMBER_PREFIX}-{date_str}-{random_str}"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth radius in kilometers
    R = 6371.0
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)

def format_currency(amount: float) -> str:
    """Format amount as AUD currency"""
    return f"${amount:.2f}"

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
```

---

#### 📄 security.py
**Path:** `app\utils\security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Ensure password is encoded and truncated to 72 bytes if necessary
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    try:
        # Ensure password is encoded and truncated to 72 bytes if necessary
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None
```

---

#### 📄 validators.py
**Path:** `app\utils\validators.py`

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate Australian phone number
    Accepts formats:
    - 0412345678 (mobile)
    - 0212345678 (landline)
    - +61412345678 (international mobile)
    - +61212345678 (international landline)
    """
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check for valid Australian phone number patterns
    # Mobile: 04XX XXX XXX or +614XX XXX XXX
    # Landline: 0[2378] XXXX XXXX or +61[2378] XXXX XXXX
    mobile_pattern = r'^(\+61|0)4\d{8}$'
    landline_pattern = r'^(\+61|0)[2378]\d{8}$'
    
    return bool(re.match(mobile_pattern, phone) or re.match(landline_pattern, phone))

def validate_postcode(postcode: str) -> bool:
    """Validate Australian postcode (4 digits)"""
    pattern = r'^\d{4}$'
    return bool(re.match(pattern, postcode))

def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None

def format_phone_for_display(phone: str) -> str:
    """Format phone number for display"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle Australian format
    if digits.startswith('61'):
        # International format: +61 4XX XXX XXX
        if len(digits) == 11 and digits[2] == '4':
            return f"+61 {digits[2:5]} {digits[5:8]} {digits[8:]}"
        # Landline: +61 2 XXXX XXXX
        elif len(digits) == 11:
            return f"+61 {digits[2]} {digits[3:7]} {digits[7:]}"
    elif digits.startswith('0'):
        # Mobile: 04XX XXX XXX
        if len(digits) == 10 and digits[1] == '4':
            return f"{digits[0:4]} {digits[4:7]} {digits[7:]}"
        # Landline: 02 XXXX XXXX
        elif len(digits) == 10:
            return f"{digits[0:2]} {digits[2:6]} {digits[6:]}"
    
    return phone  # Return as-is if format not recognized

def normalize_phone(phone: str) -> str:
    """Normalize phone number to consistent format for storage"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Convert international format to local format
    if digits.startswith('61'):
        return '0' + digits[2:]
    
    return digits
```

---

### 📁 Root

#### 📄 docs.py
**Path:** `docs.py`

```python
import os
from pathlib import Path
from datetime import datetime

def should_include_file(file_path):
    """
    Determine if a file should be included in the documentation.
    """
    # Files to exclude
    exclude_patterns = [
        '.pyc',
        '.pyo',
        '.pyd',
        '__pycache__',
        '.git',
        '.pytest_cache',
        '.coverage',
        '.env',  # Exclude actual env file for security
        '.vscode',
        '.idea',
        'venv',
        'env',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    # Check if any exclude pattern is in the path
    path_str = str(file_path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    # Include these file types
    include_extensions = [
        '.py',
        '.md',
        '.txt',
        '.yml',
        '.yaml',
        '.json',
        '.env.example',
        'Dockerfile',
        '.gitignore',
        'requirements.txt',
        'README.md'
    ]
    
    # Check if file has an included extension or is a special file
    file_name = os.path.basename(path_str)
    if file_name in ['Dockerfile', '.gitignore', 'requirements.txt', 'README.md', '.env.example']:
        return True
    
    for ext in include_extensions:
        if path_str.endswith(ext):
            return True
    
    return False

def get_language_for_file(file_path):
    """
    Get the appropriate language identifier for syntax highlighting.
    """
    extension_map = {
        '.py': 'python',
        '.md': 'markdown',
        '.txt': 'text',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.env.example': 'bash',
        'Dockerfile': 'dockerfile',
        '.gitignore': 'gitignore',
        'requirements.txt': 'text'
    }
    
    file_name = os.path.basename(file_path)
    
    # Check special files first
    if file_name in ['Dockerfile', '.gitignore', 'requirements.txt']:
        return extension_map.get(file_name, 'text')
    
    # Check by extension
    _, ext = os.path.splitext(file_path)
    return extension_map.get(ext, 'text')

def compile_backend_documentation(root_dir, output_file='backend_documentation.md'):
    """
    Compile all backend code into a single markdown file.
    
    Args:
        root_dir: The root directory of the backend project
        output_file: The output markdown file name
    """
    root_path = Path(root_dir)
    
    # Create the markdown content
    markdown_content = []
    
    # Add header
    markdown_content.append("# Backend Project Documentation\n")
    markdown_content.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    markdown_content.append(f"**Project Root:** `{root_dir}`\n")
    markdown_content.append("\n---\n\n")
    
    # Add table of contents
    markdown_content.append("## Table of Contents\n\n")
    toc_entries = []
    
    # First pass: collect all files for TOC
    all_files = []
    for root, dirs, files in os.walk(root_path):
        # Remove __pycache__ from dirs to prevent walking into it
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            file_path = Path(root) / file
            if should_include_file(file_path):
                relative_path = file_path.relative_to(root_path)
                all_files.append((file_path, relative_path))
    
    # Sort files by path for better organization
    all_files.sort(key=lambda x: str(x[1]))
    
    # Group files by directory
    current_dir = None
    for _, relative_path in all_files:
        dir_path = relative_path.parent
        
        # Add directory header if changed
        if dir_path != current_dir:
            current_dir = dir_path
            dir_name = str(dir_path) if str(dir_path) != '.' else 'Root'
            toc_entries.append(f"- **{dir_name}/**")
        
        # Add file to TOC
        anchor = str(relative_path).replace('/', '-').replace('\\', '-').replace('.', '').lower()
        toc_entries.append(f"  - [{relative_path.name}](#{anchor})")
    
    markdown_content.append('\n'.join(toc_entries))
    markdown_content.append("\n\n---\n\n")
    
    # Second pass: add file contents
    markdown_content.append("## File Contents\n\n")
    
    current_dir = None
    for file_path, relative_path in all_files:
        dir_path = relative_path.parent
        
        # Add directory section if changed
        if dir_path != current_dir:
            current_dir = dir_path
            dir_name = str(dir_path) if str(dir_path) != '.' else 'Root'
            markdown_content.append(f"### 📁 {dir_name}\n\n")
        
        # Add file content
        anchor = str(relative_path).replace('/', '-').replace('\\', '-').replace('.', '').lower()
        markdown_content.append(f"#### 📄 {relative_path.name}\n")
        markdown_content.append(f"**Path:** `{relative_path}`\n\n")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get language for syntax highlighting
            language = get_language_for_file(str(file_path))
            
            # Add code block
            markdown_content.append(f"```{language}\n")
            markdown_content.append(content)
            if not content.endswith('\n'):
                markdown_content.append('\n')
            markdown_content.append("```\n\n")
            
        except Exception as e:
            markdown_content.append(f"❌ **Error reading file:** {e}\n\n")
        
        markdown_content.append("---\n\n")
    
    # Add footer
    markdown_content.append("## Summary\n\n")
    markdown_content.append(f"**Total files documented:** {len(all_files)}\n\n")
    
    # Count by file type
    file_types = {}
    for _, relative_path in all_files:
        ext = relative_path.suffix or relative_path.name
        file_types[ext] = file_types.get(ext, 0) + 1
    
    markdown_content.append("**Files by type:**\n")
    for ext, count in sorted(file_types.items()):
        markdown_content.append(f"- {ext}: {count}\n")
    
    markdown_content.append("\n---\n")
    markdown_content.append(f"\n*Documentation generated by automated script on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_content))
    
    print(f"✅ Documentation successfully generated: {output_path.absolute()}")
    print(f"📊 Total files documented: {len(all_files)}")
    print(f"📄 Output file size: {output_path.stat().st_size / 1024:.2f} KB")

def main():
    # Set the root directory of your backend project
    backend_root = r"D:\NexusNao\CLIENTS\BAKAR\backend"
    
    # Set the output file path (will be created in the current directory)
    output_file = "backend_documentation.md"
    
    # You can also specify an absolute path for the output
    # output_file = r"D:\NexusNao\CLIENTS\BAKAR\backend_documentation.md"
    
    # Run the documentation compiler
    compile_backend_documentation(backend_root, output_file)

if __name__ == "__main__":
    main()
```

---

#### 📄 requirements.txt
**Path:** `requirements.txt`

```text
fastapi
uvicorn[standard]
motor
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
stripe
boto3
requests
googlemaps
python-dotenv
email-validator
httpx
Pillow  # For test image creation (optional)
dnspython
```

---

### 📁 scripts

#### 📄 seed_delivery_zones.py
**Path:** `scripts\seed_delivery_zones.py`

```python
"""
Seed the delivery_zones collection with the default meal-subscription coverage.

Usage:
    python backend/scripts/seed_delivery_zones.py

The script is idempotent: it only inserts records when the collection is empty.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.utils.default_delivery_zones import DEFAULT_MEAL_DELIVERY_ZONES

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bakars_food_catering")


async def seed_zones() -> None:
    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is not set. Please configure backend/.env before seeding.")

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    collection = db.delivery_zones

    try:
        existing = await collection.count_documents({})
        if existing > 0:
            print(f"Delivery zones already present ({existing} documents). Nothing to seed.")
            return

        now = datetime.utcnow()
        documents: List[Dict[str, Any]] = []

        for zone in DEFAULT_MEAL_DELIVERY_ZONES:
            payload = dict(zone)
            payload.setdefault("state", "NSW")
            payload.setdefault("order_types", ["meal_subscription"])
            payload.setdefault("is_active", True)
            payload["created_at"] = now
            payload["updated_at"] = now
            documents.append(payload)

        if not documents:
            print("No default delivery zones defined; nothing to seed.")
            return

        result = await collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} delivery zones.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_zones())
```

---

#### 📄 seed_menu_items.py
**Path:** `scripts\seed_menu_items.py`

```python
"""
Utility script to seed categories and menu items into MongoDB.

Usage:
    python backend/scripts/seed_menu_items.py
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables (backend/.env)
load_dotenv(ENV_PATH)

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "bakars_food_catering")


def item(name: str, description: str, price: float, **extras) -> Dict:
    """Helper to build menu items with consistent defaults."""
    data = {
        "name": name,
        "description": description,
        "price": price,
    }
    data.update(extras)
    return data


DEFAULT_IMAGES = {
    "rice": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop&auto=format",
    "curry": "https://images.unsplash.com/photo-1604908177571-6c4c4b47f228?w=400&h=300&fit=crop&auto=format",
    "bbq": "https://images.unsplash.com/photo-1555992336-cbf7cc116b66?w=400&h=300&fit=crop&auto=format",
    "sweets": "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop&auto=format",
    "drinks": "https://images.unsplash.com/photo-1497534446932-c925b458314e?w=400&h=300&fit=crop&auto=format",
}


CATEGORIES = [
    {
        "name": "rice",
        "display_name": "Rice Dishes",
        "description": "Aromatic biryanis, pulaos, and specialty rice dishes crafted with premium ingredients.",
        "image_url": DEFAULT_IMAGES["rice"],
        "sort_order": 1,
    },
    {
        "name": "curry",
        "display_name": "Curries & Gravies",
        "description": "Slow-cooked curries ranging from family favourites to regional signatures with rich flavours.",
        "image_url": DEFAULT_IMAGES["curry"],
        "sort_order": 2,
    },
    {
        "name": "bbq",
        "display_name": "BBQ & Grill",
        "description": "Flame-grilled meats and vegetables marinated in authentic spice blends.",
        "image_url": DEFAULT_IMAGES["bbq"],
        "sort_order": 3,
    },
    {
        "name": "sweets",
        "display_name": "Desserts",
        "description": "Celebratory desserts and sweets inspired by South Asian favourites and modern twists.",
        "image_url": DEFAULT_IMAGES["sweets"],
        "sort_order": 4,
    },
    {
        "name": "drinks",
        "display_name": "Beverages",
        "description": "Refreshing seasonal beverages, lassis, and signature coolers for every occasion.",
        "image_url": DEFAULT_IMAGES["drinks"],
        "sort_order": 5,
    },
]


BASE_MENU_ITEMS: Dict[str, List[Dict]] = {
    "rice": [
        item(
            "Signature Chicken Biryani",
            "Fragrant basmati rice with tender chicken, saffron, and caramelised onions.",
            14.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Vegetable Dum Biryani",
            "Layered vegetables and basmati rice slow-cooked in dum style with whole spices.",
            12.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Lemon Curry Leaf Rice",
            "Tangy tempered rice with mustard seeds, peanuts, and fresh lemon.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["peanuts"],
        ),
        item(
            "Jeera Tempered Rice",
            "Classic cumin-infused rice pilaf perfect for pairing with curries.",
            9.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Mutton Shahi Biryani",
            "Royal-style lamb biryani finished with ghee and saffron milk.",
            16.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Paneer Tikka Pulao",
            "Smoky paneer cubes tossed through spiced basmati rice with peppers.",
            13.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Cashew Rice",
            "Gently spiced coconut milk rice with toasted cashews and curry leaves.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Garlic Butter Rice Pilaf",
            "Golden rice sautéed with roasted garlic, herbs, and butter.",
            10.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Egg Masala Fried Rice",
            "Street-style fried rice with fluffy eggs, peppers, and scallions.",
            11.0,
            allergens=["egg", "soy"],
        ),
        item(
            "Schezwan Chicken Fried Rice",
            "Indo-Chinese fried rice tossed with fiery Schezwan sauce and chicken.",
            13.0,
            spice_level="hot",
            allergens=["soy"],
            is_halal=True,
        ),
        item(
            "Herb Infused Brown Rice",
            "Nutty brown rice cooked with fresh herbs, cumin, and roasted seeds.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Tandoori Prawn Biryani",
            "Char-grilled prawns folded through aromatic biryani rice.",
            16.0,
            spice_level="medium",
            allergens=["shellfish", "dairy"],
        ),
        item(
            "Spinach Chickpea Pilaf",
            "Protein-rich chickpeas with wilted spinach and fluffy rice.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Zafrani Chicken Pilaf",
            "Saffron scented rice with chicken morsels and toasted almonds.",
            14.0,
            allergens=["tree nuts"],
            is_halal=True,
        ),
        item(
            "Corn Methi Rice",
            "Sweet corn kernels with fenugreek leaves and mild spices.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Smoked Lamb Pilaf",
            "Smoky lamb pieces tossed with caramelised onions and basmati rice.",
            15.5,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Cashew Raisin Pulao",
            "Festive pulao dotted with raisins, cashews, and whole spices.",
            12.0,
            is_vegetarian=True,
            allergens=["tree nuts"],
        ),
        item(
            "Quinoa Vegetable Khichdi",
            "Wholesome quinoa and lentil khichdi with seasonal vegetables.",
            12.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Turmeric Coconut Rice",
            "Sunshine turmeric rice finished with coconut oil and curry leaves.",
            11.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Harvest Wild Mushroom Rice",
            "Earthy mushrooms folded through herb butter rice with pepper.",
            12.5,
            is_vegetarian=True,
        ),
    ],
    "curry": [
        item(
            "Butter Chicken Deluxe",
            "Creamy tomato gravy with tandoor-roasted chicken and fenugreek.",
            15.5,
            spice_level="mild",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Paneer Makhani Supreme",
            "Silky tomato and cashew sauce with soft paneer cubes.",
            14.0,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Lamb Rogan Josh",
            "Kashmiri-style lamb curry simmered with yogurt and aromatic spices.",
            16.5,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Goan Prawn Curry",
            "Tangy coconut curry with prawns, kokum, and curry leaves.",
            17.0,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Chickpea Masala Pot",
            "Hearty chickpeas cooked in onion-tomato masala with garam spices.",
            12.0,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Beef Madras Curry",
            "South Indian style beef curry with roasted chilies and coconut.",
            16.0,
            spice_level="hot",
        ),
        item(
            "Vegetable Korma Royale",
            "Cashew cream curry with seasonal vegetables and mild spices.",
            13.5,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["tree nuts", "dairy"],
        ),
        item(
            "Chicken Chettinad Roast",
            "Peppery Chettinad chicken with roasted coconut and curry leaves.",
            15.0,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "Palak Paneer Classic",
            "Spinach puree with cottage cheese cubes and ghee tempering.",
            13.0,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Fish Moilee Coconut",
            "Kerala coconut milk curry with fish fillets and ginger.",
            16.0,
            spice_level="medium",
            allergens=["fish"],
        ),
        item(
            "Dal Makhani Signature",
            "Slow-cooked black lentils finished with cream and butter.",
            12.5,
            spice_level="mild",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Pumpkin Coconut Curry",
            "Roasted pumpkin in spiced coconut gravy with toasted seeds.",
            12.0,
            spice_level="mild",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Chicken Tikka Masala",
            "Charcoal-grilled chicken in smoky tomato cream sauce.",
            15.0,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "Egg Masala Curry",
            "Boiled eggs simmered in spiced onion-tomato gravy.",
            12.0,
            spice_level="medium",
            allergens=["egg"],
        ),
        item(
            "Thai Green Veg Curry",
            "Lemongrass and coconut curry with Asian greens and basil.",
            14.0,
            spice_level="medium",
            is_vegetarian=True,
        ),
        item(
            "Kashmiri Dum Aloo",
            "Baby potatoes in yogurt gravy with Kashmiri chili.",
            13.0,
            spice_level="medium",
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Goat Vindaloo Fire",
            "Vinegar-marinated goat curry with bold spices and heat.",
            16.5,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "Tofu Tikka Curry",
            "Charred tofu cubes in dairy-free tikka masala sauce.",
            13.5,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Black Pepper Prawn Curry",
            "Pepper-spiced prawn curry with coconut milk and garlic.",
            17.0,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Malabar Chicken Stew",
            "Mild coconut stew with chicken, vegetables, and whole spices.",
            14.0,
            spice_level="mild",
            is_halal=True,
        ),
    ],
    "bbq": [
        item(
            "Smoky Tandoori Chicken",
            "Char-grilled chicken marinated in yogurt, chili, and garam masala.",
            15.0,
            spice_level="medium",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "BBQ Lamb Chops",
            "Tender lamb chops marinated in herbs and grilled over charcoal.",
            18.5,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Paneer Tikka Skewers",
            "Paneer cubes with peppers grilled in smoky tikka marinade.",
            14.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "BBQ Prawn Skewers",
            "Juicy prawns brushed with garlic butter and grilled.",
            17.5,
            spice_level="medium",
            allergens=["shellfish"],
        ),
        item(
            "Spicy Seekh Kebabs",
            "Ground lamb seekh kebabs with fresh herbs and chilies.",
            15.5,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "BBQ Chicken Wings",
            "Tamarind glazed wings finished with sesame smoke.",
            13.0,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "Grilled Corn Cob",
            "Charred corn brushed with lime chili seasoning.",
            8.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "BBQ Vegetable Platter",
            "Seasonal vegetables flame-grilled with smoked paprika oil.",
            12.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Charcoal Grilled Fish",
            "Whole fish with lemon herb rub grilled over charcoal.",
            18.0,
            spice_level="medium",
            allergens=["fish"],
        ),
        item(
            "BBQ Jackfruit Burnt Ends",
            "Pulled jackfruit caramelised in tangy BBQ sauce.",
            13.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Chicken Malai Tikka",
            "Creamy malai marinade with cheese, cream, and mild spices.",
            15.5,
            spice_level="mild",
            allergens=["dairy"],
            is_halal=True,
        ),
        item(
            "BBQ Beef Ribs",
            "Slow-smoked beef ribs finished with tamarind glaze.",
            19.5,
            spice_level="medium",
        ),
        item(
            "Tandoori Salmon Fillet",
            "Salmon fillet marinated in yogurt, dill, and mild chili.",
            18.5,
            spice_level="mild",
            allergens=["fish", "dairy"],
        ),
        item(
            "Peri Peri Chicken Skewers",
            "Fiery peri peri marinated chicken skewers flame-grilled.",
            15.0,
            spice_level="hot",
            is_halal=True,
        ),
        item(
            "BBQ Mushroom Medley",
            "Portobello and shiitake mushrooms with garlic herb glaze.",
            12.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Smoked Sausage Platter",
            "Assorted smoked chicken and beef sausages with mustard.",
            14.5,
            spice_level="medium",
        ),
        item(
            "BBQ Cauliflower Steaks",
            "Harissa spiced cauliflower steaks charred over grill.",
            11.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Lamb Kofta Kebabs",
            "Hand-rolled lamb kofta with mint and toasted spices.",
            16.0,
            spice_level="medium",
            is_halal=True,
        ),
        item(
            "BBQ Pineapple Rings",
            "Caramelised pineapple rings dusted with chili sugar.",
            8.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Korean BBQ Short Ribs",
            "Sweet and savoury gochujang glazed beef short ribs.",
            18.5,
            spice_level="medium",
            allergens=["soy", "sesame"],
        ),
    ],
    "sweets": [
        item(
            "Rasmalai Royale",
            "Soft paneer discs soaked in saffron cardamom milk.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Gulab Jamun Supreme",
            "Golden fried milk dumplings in rose scented syrup.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Kesar Kulfi Delight",
            "Slow churned saffron pistachio kulfi on a stick.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Mango Lassi Cheesecake",
            "Baked cheesecake with mango puree and yogurt glaze.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Cardamom Rice Kheer",
            "Creamy rice pudding simmered with almonds and saffron.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Chocolate Jalebi Sundae",
            "Crisp jalebi spirals layered with chocolate ice cream.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts", "gluten"],
        ),
        item(
            "Rose Pistachio Truffle",
            "Hand-rolled truffles with rose petals and pistachio dust.",
            6.0,
            is_vegetarian=True,
            allergens=["tree nuts"],
        ),
        item(
            "Baked Rasgulla Pudding",
            "Spongy rasgullas baked in sweet custard and caramel.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Barfi Bites",
            "Toasted coconut fudge squares with cardamom.",
            6.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Masala Chai Tiramisu",
            "Fusion tiramisu soaked in masala chai syrup.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Saffron Phirni Cups",
            "Ground rice pudding served chilled with pistachios.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Kesari Sheera Pots",
            "Semolina pudding with ghee, saffron, and cashews.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Chocolate Chai Brownie",
            "Fudgy brownie infused with chai spice blend.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Pistachio Baklava Cups",
            "Mini baklava bites with pistachio and honey drizzle.",
            7.5,
            is_vegetarian=True,
            allergens=["tree nuts", "gluten"],
        ),
        item(
            "Malai Sandwich Delight",
            "Layered Bengali sweet with clotted cream filling.",
            7.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Carrot Halwa Tart",
            "Butter tart shell filled with gajar halwa and nuts.",
            8.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts", "gluten"],
        ),
        item(
            "Masala Panna Cotta",
            "Vanilla panna cotta finished with cardamom caramel.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Coconut Jaggery Payasam",
            "Coconut milk payasam with jaggery and roasted cashews.",
            6.5,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Saffron Basque Cheesecake",
            "Burnt basque cheesecake with saffron accents.",
            8.5,
            is_vegetarian=True,
            allergens=["dairy", "gluten"],
        ),
        item(
            "Rose Falooda Parfait",
            "Layered falooda with basil seeds, jelly, and kulfi.",
            7.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
    ],
    "drinks": [
        item(
            "Rose Cardamom Lassi",
            "Refreshing yogurt drink blended with rose syrup and cardamom.",
            6.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Mango Mint Cooler",
            "Chilled mango nectar with muddled mint and lime.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Masala Chaas",
            "Spiced buttermilk with toasted cumin and coriander.",
            5.0,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Kesar Pista Milkshake",
            "Rich saffron pistachio milkshake topped with nuts.",
            6.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Tamarind Ginger Spritz",
            "Sweet and tangy tamarind cooler with ginger fizz.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Filter Coffee Frappe",
            "Iced frappe prepared with South Indian filter coffee.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Lychee Rose Sangria",
            "Non-alcoholic sangria with lychee, rose, and citrus.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Masala Lime Soda",
            "Sparkling lime soda seasoned with chaat masala.",
            4.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Kokum Mint Cooler",
            "Konkan-style kokum sherbet with mint and jaggery.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Saffron Badam Milk",
            "Warm almond milk infused with saffron and cardamom.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Cold Brew Spice Latte",
            "Cold brew coffee with cinnamon, star anise, and cream.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Pineapple Jalapeno Refresher",
            "Sweet pineapple cooler balanced with jalapeno heat.",
            5.5,
            spice_level="medium",
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Thandai Festival Shake",
            "Festival favourite with soaked nuts and fennel.",
            6.0,
            is_vegetarian=True,
            allergens=["dairy", "tree nuts"],
        ),
        item(
            "Cucumber Basil Cooler",
            "Hydrating cucumber juice with basil and lime.",
            4.8,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Turmeric Golden Latte",
            "Anti-inflammatory turmeric latte with honey and pepper.",
            5.5,
            is_vegetarian=True,
            allergens=["dairy"],
        ),
        item(
            "Spiced Apple Punch",
            "Warm apple punch with cinnamon, cloves, and citrus.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Jamun Kala Khatta Slush",
            "Vibrant black plum slush with tangy spice blend.",
            5.0,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Caramel Date Shake",
            "Smooth date shake blended with caramel and almond milk.",
            6.0,
            is_vegetarian=True,
            is_vegan=True,
            allergens=["tree nuts"],
        ),
        item(
            "Lemongrass Iced Tea",
            "Refreshing iced tea brewed with lemongrass and lime.",
            4.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
        item(
            "Rose Coconut Smoothie",
            "Creamy coconut milk smoothie perfumed with rose water.",
            5.5,
            is_vegetarian=True,
            is_vegan=True,
        ),
    ],
}


def get_menu_items() -> Dict[str, List[Dict]]:
    """Return deep copies of the seed menu items to avoid mutation."""
    return {category: [dict(item_) for item_ in items] for category, items in BASE_MENU_ITEMS.items()}


async def seed_categories(db) -> Dict[str, str]:
    """Insert or update categories and return their IDs."""
    categories_collection = db.categories
    category_ids: Dict[str, str] = {}

    for category in CATEGORIES:
        existing = await categories_collection.find_one({"name": category["name"]})
        payload = {
            **category,
            "is_active": True,
            "updated_at": datetime.utcnow(),
        }
        if existing:
            await categories_collection.update_one({"_id": existing["_id"]}, {"$set": payload})
            category_ids[category["name"]] = str(existing["_id"])
        else:
            payload["created_at"] = datetime.utcnow()
            result = await categories_collection.insert_one(payload)
            category_ids[category["name"]] = str(result.inserted_id)

    return category_ids


def build_menu_item_payload(item_data: Dict, category: str) -> Dict:
    """Prepare a menu item document ready for insert/update."""
    now = datetime.utcnow()
    payload = {
        "name": item_data["name"],
        "description": item_data.get("description"),
        "category": category,
        "price": float(item_data["price"]),
        "image_url": item_data.get("image_url", DEFAULT_IMAGES.get(category)),
        "is_available": item_data.get("is_available", True),
        "is_available_for_daily": item_data.get("is_available_for_daily", True),
        "is_available_for_meal_plan": item_data.get("is_available_for_meal_plan", True),
        "allergens": item_data.get("allergens", []),
        "spice_level": item_data.get("spice_level"),
        "is_vegetarian": item_data.get("is_vegetarian", False),
        "is_vegan": item_data.get("is_vegan", False),
        "is_halal": item_data.get("is_halal", True),
        "nutritional_info": item_data.get("nutritional_info"),
        "serving_size": item_data.get("serving_size", "Single serve"),
        "created_at": now,
        "updated_at": now,
    }
    return payload


async def seed_menu_items(db):
    """Ensure each category has at least 20 menu items."""
    menu_collection = db.menu_items
    menu_items = get_menu_items()

    for category, items in menu_items.items():
        for item_data in items:
            payload = build_menu_item_payload(item_data, category)
            existing = await menu_collection.find_one({"name": payload["name"], "category": category})
            if existing:
                payload["created_at"] = existing.get("created_at", payload["created_at"])
                await menu_collection.update_one({"_id": existing["_id"]}, {"$set": payload})
            else:
                await menu_collection.insert_one(payload)

        count = await menu_collection.count_documents({"category": category})
        if count < 20:
            raise RuntimeError(f"Category '{category}' has only {count} items after seeding.")


async def main():
    if not MONGODB_URL:
        raise EnvironmentError("MONGODB_URL is not configured. Check backend/.env.")

    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]

    try:
        await client.admin.command("ping")
        print("MongoDB connection successful.")

        category_ids = await seed_categories(db)
        print(f"Upserted categories: {', '.join(category_ids.keys())}")

        await seed_menu_items(db)

        menu_collection = db.menu_items
        print("\nMenu item counts by category:")
        for category in BASE_MENU_ITEMS.keys():
            count = await menu_collection.count_documents({"category": category})
            print(f" - {category}: {count} items")

        print("\nSeeding completed successfully.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary

**Total files documented:** 63

**Files by type:**
- .md: 2
- .py: 59
- .txt: 1
- Dockerfile: 1

---

*Documentation generated by automated script on 2025-11-13 20:04:56*