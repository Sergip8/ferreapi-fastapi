from fastapi import APIRouter

from app.api.routes import login, private, users, utils, categories, products
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])



if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
