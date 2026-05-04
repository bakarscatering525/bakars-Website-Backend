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
