from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

# Instanciamos la ruta de este controlador
router = APIRouter()

# Creamos las instancias de las capas (Inyección de dependencias manual)
user_repository = UserRepository()
user_service = UserService(user_repository=user_repository)

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    Get all registered users.
    """
    return user_service.get_users(db=db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    return user_service.get_user_by_id(user_id=user_id, db=db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    return user_service.create_user(user_in=user_in, db=db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user by Id.
    """
    return user_service.update_user(user_id=user_id, user_in=user_in, db=db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    """
    user_service.delete_user(user_id=user_id, db=db)
    return None