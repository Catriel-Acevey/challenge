from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

# Instanciamos la ruta de este controlador
router = APIRouter()

# Creamos las instancias de las capas (Inyección de dependencias manual)
user_repository = UserRepository()
user_service = UserService(user_repository=user_repository)

@router.get("/", response_model=list[UserResponse])
def get_users():
    """
    Get all registered users.
    """
    return user_service.get_users()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """
    Get a specific user by ID.
    """
    return user_service.get_user_by_id(user_id)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    """
    Register a new user.
    """
    return user_service.create_user(user_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """
    Delete a user by ID.
    """
    user_service.delete_user(user_id)
    return None