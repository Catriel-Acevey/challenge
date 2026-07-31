from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

# Register the users endpoints router with its prefix and documentation tags
api_router.include_router(users.router, prefix="/users", tags=["users"])