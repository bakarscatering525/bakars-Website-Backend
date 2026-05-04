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
