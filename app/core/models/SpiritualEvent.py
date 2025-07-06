from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field

class SpiritualEvent(Document):
    id: str = Field(alias="_id")
    eventTitle: Indexed(str)
    shortDescription: str
    longDescription: str
    mainImage: str
    additionalImages: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default=None)
    eventDate: datetime
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SpiritualEvent {self.eventTitle}>"

    class Settings:
        name = "spiritual_events"
