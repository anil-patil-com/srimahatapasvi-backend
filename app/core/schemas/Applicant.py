from typing import List
from pydantic import BaseModel

class ApplicantCreate(BaseModel):
    fullName: str
    Address: str
    contactNumber: str
    dateOfBirth: str

class ApplicantResponse(BaseModel):
    id: str
    fullName: str
    Address: str
    contactNumber: str
    dateOfBirth: str

    class Config:
        from_attributes = True

class ApplicantListResponse(BaseModel):
    applicants: List[ApplicantResponse]
    total: int
