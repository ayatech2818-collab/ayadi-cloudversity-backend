from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseBrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    slug: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    is_active: bool = True
    display_order: int = 0


class CourseBrandCreate(CourseBrandBase):
    pass


class CourseBrandUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class CourseBrandResponse(CourseBrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    logo_url: str | None = None
    created_at: datetime
    updated_at: datetime