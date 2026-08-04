from typing import Optional, List
from pydantic import BaseModel, EmailStr

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

    class Config:
        from_attributes = True