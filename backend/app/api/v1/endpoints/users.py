from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import user_service
from app.repositories.user_repository import UserRepository

router = APIRouter()

user_repository = UserRepository()

@router.get("/", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """
    Get all registered users.
    """
    return await user_service.get_users(db=db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    return await user_service.get_user_by_id(user_id=user_id, db=db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    return await user_service.create_user(user_in=user_in, db=db)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user by Id.
    """
    return await user_service.update_user(user_id=user_id, user_in=user_in, db=db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    """
    user_service.delete_user(user_id=user_id, db=db)
    return None