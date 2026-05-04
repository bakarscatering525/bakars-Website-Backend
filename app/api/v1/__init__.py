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
