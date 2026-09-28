from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.gallery.models.gallery_item import GalleryMediaType


class GalleryItemUpdate(BaseModel):
    alt_text: str | None = Field(
        default=None,
        max_length=255,
    )
    display_order: int | None = Field(
        default=None,
        ge=0,
    )


class GalleryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    gallery_id: UUID
    file_name: str
    file_url: str
    media_type: GalleryMediaType
    mime_type: str
    file_size: int | None
    alt_text: str | None
    display_order: int
    created_at: datetime
    updated_at: datetime