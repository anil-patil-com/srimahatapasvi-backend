from typing import Optional
from pydantic import BaseModel, EmailStr, Field, Extra, validator
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PA = "pa"
    LEAD = "lead"

class UserBase(BaseModel):
    name: str = Field(..., description="Full name of the user")
    userName: str = Field(..., description="Unique username for login")
    phoneNumber: str = Field(..., description="Phone number with country code")
    role: UserRole = Field(default=UserRole.USER, description="User role in the system")

    @validator('phoneNumber')
    def validate_phone(cls, v):
        # Remove any spaces or special characters
        v = ''.join(filter(str.isdigit, v))
        if not v.startswith('+'):
            v = '+' + v
        if len(v) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password for authentication")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phoneNumber: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    isActive: Optional[bool] = None
    isSuperuser: Optional[bool] = None

class UserResponse(UserBase):
    class Config:
        populate_by_name = True
        from_attributes = True
        
    id: str = Field(alias="_id")
    isActive: bool
    isSuperuser: bool
    createdAt: datetime
    updatedAt: datetime

class UserListResponse(BaseModel):
    class Config:
        extra = Extra.forbid

    total: int
    items: list[UserResponse]

class Token(BaseModel):
    userId: str
    accessToken: str
    tokenType: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int

class UserLogin(BaseModel):
    userName: str
    password: str
