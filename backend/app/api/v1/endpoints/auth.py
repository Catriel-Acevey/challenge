from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserCreate, AuthResponse, LoginRequest
from app.services.user_service import user_service

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Register a new user in the system using user_service."""
    return await user_service.register_user(db=db, user_in=user_in)

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    return user_service.login_user(
        db=db, email=form_data.username, password=form_data.password
    )
