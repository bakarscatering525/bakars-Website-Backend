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
    "http://localhost:5174",
    "http://127.0.0.1:5174",
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
