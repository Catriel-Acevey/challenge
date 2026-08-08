from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Fetch a single user by their primary key ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        return db.query(User).filter(User.email == email).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve a list of users with pagination parameters."""
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, user_data: UserCreate) -> User:
        """Create and persist a new user in the database."""
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            pokemon_team=user_data.pokemon_team
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_user: User, user_data: UserUpdate) -> User:
        """Update an existing user's details."""
        update_data = user_data.model_dump(exclude_unset=True)
        
        print(f"updating user: {update_data.items()}")

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, db_user: User) -> None:
        """Delete a user from the database."""
        db.delete(db_user)
        db.commit()