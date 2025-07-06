from datetime import datetime
from uuid import uuid4
from typing import Optional
from beanie import Document, Indexed, Link
from pydantic import Field
from app.core.schemas.Darshan import DarshanStatus
from app.core.models.User import User

class Darshan(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phoneNumber: Indexed(str)
    address: str
    reasonToVisit: str
    numberOfPeople: int
    status: str = Field(default=DarshanStatus.PENDING_LEAD)
    scheduledDateTime: Optional[datetime] = None
    scheduledLocation: Optional[str] = None
    reason: Optional[str] = None
    leadId: str  # Reference to the lead user
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "darshan_requests"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "phoneNumber": "+919876543210",
                "address": "123 Main St, City, Country",
                "reasonToVisit": "Spiritual guidance",
                "numberOfPeople": 2,
                "status": "pending_lead",
                "leadId": "lead_user_id",
                "createdBy": "user_id"
            }
        }
