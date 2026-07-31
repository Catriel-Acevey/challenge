from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def get_users(self) -> List[dict]:
        """
        Retrieves all users.
        """
        return self.user_repo.get_all()

    def get_user_by_id(self, user_id: int) -> dict:
        """
        Retrieves a user by ID or raises 404 if not found.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return user

    def create_user(self, user_in: UserCreate) -> dict:
        """
        Validates email uniqueness and creates a new user.
        """
        existing_user = self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        user_data = user_in.model_dump()
        return self.user_repo.create(user_data)

    def delete_user(self, user_id: int) -> None:
        """
        Deletes a user by ID or raises 404 if not found.
        """
        success = self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )