from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Register the authentication endpoints router with its prefix and documentation tags
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# Register the users endpoints router with its prefix and documentation tags
api_router.include_router(users.router, prefix="/users", tags=["users"])