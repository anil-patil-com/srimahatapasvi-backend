from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from fastapi import UploadFile, File, Form

class EventType(str, Enum):
    social = "social"
    educational = "educational"
    cultural = "cultural"

class EventBase(BaseModel):
    eventTitle: str
    shortDescription: str
    longDescription: str
    eventType: EventType
    eventDate: datetime

class EventCreateRequest(EventBase):
    eventTitle: str = Form(...)
    shortDescription: str = Form(...)
    longDescription: str = Form(...)
    eventType: EventType = Form(...)
    eventDate: datetime = Form(...)

class EventUpdateRequest(BaseModel):
    eventTitle: Optional[str] = Form(None)
    shortDescription: Optional[str] = Form(None)
    longDescription: Optional[str] = Form(None)
    eventType: Optional[EventType] = Form(None)
    eventDate: Optional[datetime] = Form(None)

class EventResponse(EventBase):
    class Config:
        populate_by_name = True
        
    id: str = Field(alias="_id")
    mainImage: str
    additionalImages: List[str]
    videos: Optional[List[str]] = Field(default=None) 
    createdAt: datetime
    updatedAt: datetime

class EventListResponse(BaseModel):
    class Config:
        extra = Extra.forbid

    total: int
    items: list[EventResponse]
