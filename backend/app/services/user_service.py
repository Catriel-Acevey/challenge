from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt
from pydantic import ValidationError

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.clients.pokeapi import PokeAPIClient, poke_api_client
from app.core import security
from app.core.config import settings


class UserService:
    def __init__(self, user_repository: UserRepository, poke_client: PokeAPIClient):
        self.user_repo = user_repository
        self.poke_client = poke_client
        
    async def register_user(self, db: Session, user_in: UserCreate) -> dict:
            """Check business rules and delegate creation to repository."""
    
            if self.user_repo.get_by_email(db, email=user_in.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The user with this email already exists in the system.",
                )
    
            hashed_password = security.get_password_hash(user_in.password)
            user_data = {
                "email": user_in.email,
                "username": user_in.username,
                "hashed_password": hashed_password,
                "pokemon_team": user_in.pokemon_team or [],
            }
            user = self.user_repo.create(db, user_data=user_data)
            
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = security.create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
                user.pokemon_team or []
            )
            return {
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    pokemon_team=pokemon_names or [],
                ),
                "token": {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            }

    async def create_user(self, db: Session, user_in: UserCreate) -> dict:
        """Check business rules and delegate creation to repository."""

        if self.user_repo.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )

        hashed_password = security.get_password_hash(user_in.password)
        user_data = {
            "email": user_in.email,
            "username": user_in.username,
            "hashed_password": hashed_password,
            "pokemon_team": user_in.pokemon_team or [],
        }
        user = self.user_repo.create(db, user_data=user_data)

        pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
            user.pokemon_team or []
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            pokemon_team=pokemon_names or [],
        )
        
    def login_user(self, db: Session, email: str, password: str) -> dict:
        """Authenticate user credentials and return access token."""
        # 1. Fetch user
        user = self.user_repo.get_by_email(db, email=email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email/username or password",
            )

        # 2. Check active state
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        # 3. Build token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieves all users with pagination."""
        users = self.user_repo.get_all(db=db, skip=skip, limit=limit)
        enriched_users = []
        for user in users:
            pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
                user.pokemon_team or []
            )
            enriched_users.append(
                UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    pokemon_team=pokemon_names or []
                )
            )
        return enriched_users

    async def get_user_by_id(self, db: Session, user_id: int) -> User:
        """Retrieves a user by ID or raises 404 if not found."""
        user = self.user_repo.get_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
            user.pokemon_team or []
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            pokemon_team=pokemon_names or []
        )

    async def get_user_from_token(self, db: Session, token: str) -> User:
        """Extracts the user from the JWT token or raises 401/404 if invalid."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise self._credentials_exception()
        except (jwt.PyJWTError, ValidationError):
            raise self._credentials_exception()

        user = self.user_repo.get_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
            user.pokemon_team or []
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            pokemon_team=pokemon_names or []
        )

    async def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> User:
        """Updates an existing user or raises 404."""
        db_user = self.user_repo.get_by_id(db=db, user_id=user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = self.user_repo.update(db=db, db_user=db_user, user_data=user_in)
        enriched_pokemon_names = await self.poke_client.get_pokemon_names_by_ids(
            user.pokemon_team or []
        )
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            pokemon_team=enriched_pokemon_names or [],
            is_active=user.is_active,
        )

    def delete_user(self, db: Session, user_id: int) -> None:
        """Deletes a user by ID or raises 404 if not found."""
        db_user = self.user_repo.get_by_id(db=db, user_id=user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        self.user_repo.delete(db=db, db_user=db_user)


user_repository = UserRepository()
user_service = UserService(user_repository=user_repository, poke_client=poke_api_client)