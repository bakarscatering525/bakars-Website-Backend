from fastapi import APIRouter, HTTPException, status, Depends, Request
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

LOCAL_HOST_MARKERS = ("localhost", "127.0.0.1")


def _resolve_frontend_base_url(request: Request) -> str:
    """
    Determine the best base URL for password reset links.
    Priority:
    1. FRONTEND_BASE_URL env (when not localhost)
    2. Origin/Referer header from the request
    3. Host header using scheme/X-Forwarded-Proto
    4. Production domain fallback
    """
    configured = (settings.FRONTEND_BASE_URL or "").strip().rstrip("/")
    if configured and not any(host in configured for host in LOCAL_HOST_MARKERS):
        return configured

    header_origin = (
        request.headers.get("origin")
        or request.headers.get("referer")
        or request.headers.get("Origin")
        or request.headers.get("Referer")
    )
    if header_origin:
        header_origin = header_origin.rstrip("/")
        if not any(host in header_origin for host in LOCAL_HOST_MARKERS):
            return header_origin

    host_header = request.headers.get("host") or request.headers.get("Host")
    proto = (
        request.headers.get("x-forwarded-proto")
        or request.headers.get("X-Forwarded-Proto")
        or request.url.scheme
    )
    if host_header:
        host_header = host_header.strip()
        if not any(host in host_header for host in LOCAL_HOST_MARKERS):
            return f"{proto}://{host_header}".rstrip("/")

    return "https://www.bakarsfood.com"

@router.post("/register", response_model=ApiResponse[RegistrationResponse])
async def register(user_data: UserRegisterRequest):
    """Register a new user and send verification email"""
    try:
        user = await auth_service.register_user(user_data)
        
        # Generate verification code
        code = await auth_service.generate_verification_code(user.email)
        
        # Send verification email (do not fail registration if email sending times out)
        email_sent = True
        try:
            await send_verification_email(
                email=user.email,
                name=user.first_name,
                code=code
            )
        except Exception as send_error:
            email_sent = False
            logger.error("Registration email send failed for %s: %s", user.email, send_error)
        
        message = (
            "Registration successful! Please check your email for verification code."
            if email_sent
            else "Registration successful, but we could not send the verification email. Please try resending the code."
        )

        return ApiResponse(
            success=True,
            data=RegistrationResponse(
                email=user.email,
                message=message
            ),
            message=message
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
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    """Initiate password reset and send email with link."""
    try:
        token, user = await auth_service.create_password_reset_request(payload.email)
        message = "If an account exists for this email, a reset link has been sent."
        base_url = _resolve_frontend_base_url(request)
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
