from fastapi import APIRouter

from app.api.v1.endpoints import auth, notifications, users

api_router = APIRouter()

# Register the authentication endpoints router with its prefix and documentation tags
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# Register the users endpoints router with its prefix and documentation tags
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Register the notifications endpoints router with its prefix and documentation tags
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"],
)
