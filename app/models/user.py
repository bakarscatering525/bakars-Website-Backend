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
