from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import Field

from app.core.schemas.Event import EventType

class Event(Document):
    id: str = Field(alias="_id")
    eventTitle: Indexed(str)
    shortDescription: str
    longDescription: str
    eventType: EventType
    eventDate: datetime
    mainImage: str
    additionalImages: List[str] = Field(default=None)
    videos: Optional[List[str]] = Field(default=None)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Event {self.eventTitle}>"

    class Settings:
        name = "events"
