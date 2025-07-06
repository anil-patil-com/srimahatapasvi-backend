from typing import Optional
from pydantic import BaseModel, Field, Extra
from datetime import datetime
from fastapi import UploadFile, File, Form

class TeamMemberBase(BaseModel):
    name: str
    role: str
    description: str

class TeamMemberCreateRequest(BaseModel):
    name: str = Form(...)
    role: str = Form(...)
    description: str = Form(...)

class TeamMemberUpdateRequest(BaseModel):
    name: Optional[str] = Form(None)
    role: Optional[str] = Form(None)
    description: Optional[str] = Form(None)

class TeamMemberResponse(TeamMemberBase):
    class Config:
        populate_by_name = True
        
    id: str = Field(alias="_id")
    image: str
    createdAt: datetime
    updatedAt: datetime

class TeamMemberListResponse(BaseModel):
    class Config:
        extra = Extra.forbid

    total: int
    items: list[TeamMemberResponse]
