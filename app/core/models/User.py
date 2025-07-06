from datetime import datetime
from uuid import uuid4
from beanie import Document, Indexed
from pydantic import Field
from app.core.schemas.User import UserRole

class User(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    userName: Indexed(str, unique=True)  # Make username unique
    phoneNumber: str
    role: UserRole = Field(default=UserRole.USER)
    password: str
    isActive: bool = True
    isSuperuser: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.userName}>"

    class Settings:
        name = "users"
        
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "userName": "johndoe123",
                "phoneNumber": "+919876543210",
                "role": "user",
                "hashed_password": "hashedpass123",
                "isActive": True,
                "isSuperuser": False
            }
        }
