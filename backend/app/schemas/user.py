from pydantic import BaseModel, EmailStr

# Base schema with shared attributes
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Schema for creating a user (Input)
class UserCreate(UserBase):
    password: str

# Schema for returning user data (Output)
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True