from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GalleryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = None
    event_date: date | None = None
    is_published: bool = False


class GalleryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    event_date: date | None = None
    is_published: bool | None = None


class GalleryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    description: str | None
    event_date: date | None
    is_published: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime