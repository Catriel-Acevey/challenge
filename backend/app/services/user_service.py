from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.clients.pokeapi import PokeAPIClient, poke_api_client


class UserService:
    def __init__(self, user_repository: UserRepository, poke_client: PokeAPIClient):
        self.user_repo = user_repository
        self.poke_client = poke_client

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

    async def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Validates email uniqueness and creates a new user."""
        existing_user = self.user_repo.get_by_email(db=db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
            
        user = self.user_repo.create(db=db, user_data=user_in)
        
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