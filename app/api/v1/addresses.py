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
