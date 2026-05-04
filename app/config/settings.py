import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
_LOCAL_HOST_MARKERS = ("localhost", "127.0.0.1")


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _default_frontend_base_url() -> str:
    """
    Provide a production-safe fallback so password reset links don't point to localhost.
    """
    if _ENVIRONMENT.lower() == "production":
        return "https://www.bakarsfood.com"
    return "http://localhost:5173"


def _resolve_frontend_base_url_from_env() -> str:
    """
    Read FRONTEND_BASE_URL from the environment but automatically upgrade
    localhost values when running in production.
    """
    configured = (os.getenv("FRONTEND_BASE_URL") or "").strip()
    if not configured:
        return _default_frontend_base_url()

    if _ENVIRONMENT.lower() == "production" and any(
        marker in configured for marker in _LOCAL_HOST_MARKERS
    ):
        return "https://www.bakarsfood.com"

    return configured


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
    STRIPE_TEST_SECRET_KEY: str = os.getenv("STRIPE_TEST_SECRET_KEY", "")
    STRIPE_TEST_PUBLISHABLE_KEY: str = os.getenv("STRIPE_TEST_PUBLISHABLE_KEY", "")
    STRIPE_TEST_WEBHOOK_SECRET: str = os.getenv("STRIPE_TEST_WEBHOOK_SECRET", "")
    STRIPE_TEST_MODE: bool = _env_bool(
        "STRIPE_TEST_MODE",
        "true" if os.getenv("ENVIRONMENT", "development") != "production" else "false",
    )
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
    BUSINESS_TIMEZONE: str = os.getenv("BUSINESS_TIMEZONE", "Australia/Sydney")
    
    # SMTP / Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", ""))
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Bakar's Food & Catering")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    CONTACT_RECIPIENT_EMAIL: str = os.getenv("CONTACT_RECIPIENT_EMAIL", os.getenv("SMTP_FROM_EMAIL", ""))
    FRONTEND_BASE_URL: str = _resolve_frontend_base_url_from_env()
    ORDER_NOTIFICATIONS_EMAIL: str = os.getenv("ORDER_NOTIFICATIONS_EMAIL", "bakarfoods@gmail.com")
    
    # CORS - Hardcoded for simplicity
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Environment
    ENVIRONMENT: str = _ENVIRONMENT
    
    # Reminder scheduler
    ENABLE_REMINDER_SCHEDULER: bool = os.getenv("ENABLE_REMINDER_SCHEDULER", "true").lower() == "true"
    REMINDER_SCHEDULER_INTERVAL_SECONDS: int = int(os.getenv("REMINDER_SCHEDULER_INTERVAL_SECONDS", "1800"))
    PURGE_LEGACY_MEAL_PLANS: bool = os.getenv("PURGE_LEGACY_MEAL_PLANS", "false").lower() == "true"

    @property
    def use_test_stripe_keys(self) -> bool:
        """Return True only when test mode is enabled and keys are provided."""
        return (
            self.STRIPE_TEST_MODE
            and bool(self.STRIPE_TEST_SECRET_KEY)
            and bool(self.STRIPE_TEST_PUBLISHABLE_KEY)
        )

    @property
    def active_stripe_secret_key(self) -> str:
        if self.use_test_stripe_keys:
            return self.STRIPE_TEST_SECRET_KEY
        return self.STRIPE_SECRET_KEY

    @property
    def active_stripe_publishable_key(self) -> str:
        if self.use_test_stripe_keys:
            return self.STRIPE_TEST_PUBLISHABLE_KEY
        return self.STRIPE_PUBLISHABLE_KEY

    @property
    def active_stripe_webhook_secret(self) -> str:
        if self.use_test_stripe_keys:
            return self.STRIPE_TEST_WEBHOOK_SECRET
        return self.STRIPE_WEBHOOK_SECRET

    @property
    def is_live_stripe_mode(self) -> bool:
        """True when the app is operating with live keys."""
        active_secret = self.active_stripe_secret_key
        return bool(active_secret) and not self.use_test_stripe_keys

# Create settings instance
settings = Settings()
