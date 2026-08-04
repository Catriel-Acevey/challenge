from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieves all users with pagination."""
        return self.user_repo.get_all(db=db, skip=skip, limit=limit)

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """Retrieves a user by ID or raises 404 if not found."""
        user = self.user_repo.get_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return user

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Validates email uniqueness and creates a new user."""
        existing_user = self.user_repo.get_by_email(db=db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        return self.user_repo.create(db=db, user_data=user_in)

    def update_user(self, db: Session, user_id: int, user_in: UserUpdate) -> User:
        """Updates an existing user or raises 404."""
        db_user = self.get_user_by_id(db=db, user_id=user_id)
        return self.user_repo.update(db=db, db_user=db_user, user_data=user_in)

    def delete_user(self, db: Session, user_id: int) -> None:
        """Deletes a user by ID or raises 404 if not found."""
        db_user = self.get_user_by_id(db=db, user_id=user_id)
        self.user_repo.delete(db=db, db_user=db_user)


user_repository = UserRepository()
user_service = UserService(user_repository=user_repository)