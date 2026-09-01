from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

# Base schema with shared attributes
class UserBase(BaseModel):
    email: EmailStr
    username: str
    pokemon_team: Optional[List[int]] = None

# Schema for creating a user (Input)
class UserCreate(UserBase):
    password: str

# Schema for updating a user (Input - Partial Updates)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    pokemon_team: Optional[List[int]] = None
    password: Optional[str] = None

# Schema for returning user data (Output)
class UserResponse(UserBase):
    id: int
    is_active: bool
    pokemon_team: List[str] = []

    model_config = ConfigDict(from_attributes=True)
    
# Schema for returning the JWT access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schema for decoding token payload internally
class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Schema for returning user data along with the JWT token
class AuthResponse(BaseModel):
    user: UserResponse
    token: Token
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str