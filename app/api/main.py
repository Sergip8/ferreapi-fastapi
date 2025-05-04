from fastapi import APIRouter

from app.api.routes import category, inventory, login, order, private, promotion, raw_material_inventory, shipping_delivery, supplier, technical_specification, users, utils, categories, products
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(technical_specification.router, prefix="/technical-specifications", tags=["technical-specifications"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(raw_material_inventory.router, prefix="/raw-material-inventory", tags=["raw-material-inventory"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(shipping_delivery.router, prefix="/shipping-delivery", tags=["shipping-delivery"])
api_router.include_router(promotion.router, prefix="/promotions", tags=["promotions"])








if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
