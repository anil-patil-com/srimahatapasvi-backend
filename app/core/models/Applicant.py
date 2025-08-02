from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field

class Applicant(Document):
    id: str = Field(alias="_id")
    fullName: str
    dateOfBirth: datetime
    Address: str
    contactNumber: str

    def __repr__(self) -> str:
        return f"<SpiritualEvent {self.eventTitle}>"

    class Settings:
        name = "spiritual_events"
