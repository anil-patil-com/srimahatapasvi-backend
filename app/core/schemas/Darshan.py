from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator

class DarshanStatus(str, Enum):
    PENDING_LEAD = "A1"
    PENDING_PA = "A2"
    APPROVED = "A3"
    REJECTED = "A4"

class DarshanBase(BaseModel):
    name: str = Field(..., description="Name of the person requesting darshan")
    phoneNumber: str = Field(..., description="Contact number")
    address: str = Field(..., description="Address of the person")
    reasonToVisit: str = Field(..., description="Reason for requesting darshan")
    numberOfPeople: int = Field(..., gt=0, description="Number of people for darshan")
    leadId: str = Field(..., description="ID of the lead to approve the request")

    @validator('phoneNumber')
    def validate_phone(cls, v):
        # Remove any spaces or special characters
        v = ''.join(filter(str.isdigit, v))
        if not v.startswith('+'):
            v = '+' + v
        if len(v) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v

    @validator('numberOfPeople')
    def validate_number_of_people(cls, v):
        if v <= 0:
            raise ValueError('Number of people must be greater than 0')
        return v

class DarshanCreate(DarshanBase):
    pass

class DarshanLeadApprovalUpdate(BaseModel):
    status: bool
    reason: str

class DarshanUpdate(BaseModel):
    status: bool
    scheduledDateTime: Optional[datetime] = None
    scheduledLocation: Optional[str] = None
    reason: str = None

class DarshanResponse(DarshanBase):
    id: str
    status: DarshanStatus
    scheduledDateTime: Optional[datetime]
    scheduledLocation: Optional[str]
    reason: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True

class DarshanListResponse(BaseModel):
    total: int
    items: list[DarshanResponse]
