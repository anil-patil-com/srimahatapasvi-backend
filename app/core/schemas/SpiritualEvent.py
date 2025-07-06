from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from fastapi import UploadFile, File, Form

class SpiritualEventBase(BaseModel):
    eventTitle: str
    shortDescription: str
    longDescription: str
    eventDate: datetime

class SpiritualEventCreate(BaseModel):
    eventTitle: str = Form(...)
    shortDescription: str = Form(...)
    longDescription: str = Form(...)
    eventDate: datetime = Form(...)

class SpiritualEventUpdate(BaseModel):
    eventTitle: Optional[str] = Form(None)
    shortDescription: Optional[str] = Form(None)
    longDescription: Optional[str] = Form(None)
    eventDate: Optional[datetime] = Form(None)

class SpiritualEventResponse(SpiritualEventBase):
    class Config:
        populate_by_name = True
        
    id: str = Field(alias="_id")
    mainImage: str
    additionalImages: List[str]
    videos: Optional[List[str]] = Field(default=None) 
    createdAt: datetime
    updatedAt: datetime

class SpiritualEventListResponse(BaseModel):
    class Config:
        extra = Extra.forbid

    total: int
    items: list[SpiritualEventResponse]
