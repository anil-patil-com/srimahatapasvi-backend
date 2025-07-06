from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

class TeamMember(Document):
    id: str = Field(alias="_id")
    name: Indexed(str)
    role: str
    description: str
    image: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TeamMember {self.name}>"

    class Settings:
        name = "team_members"
