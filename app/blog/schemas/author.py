import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    designation: str | None = Field(default=None, max_length=255)
    bio: str | None = None
    profile_image: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    designation: str | None = Field(default=None, max_length=255)
    bio: str | None = None
    profile_image: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    designation: str | None
    bio: str | None
    profile_image: str | None
    linkedin_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime