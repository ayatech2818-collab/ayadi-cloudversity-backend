from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    brand_id: UUID
    category_id: UUID
    subcategory_id: UUID

    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    course_code: str = Field(..., min_length=1, max_length=50)

    short_description: str | None = None
    description: str | None = None

    duration: str | None = Field(
        default=None,
        max_length=100,
    )

    level: str | None = Field(
        default=None,
        max_length=50,
    )

    is_published: bool = False
    display_order: int = 0


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    brand_id: UUID | None = None
    category_id: UUID | None = None
    subcategory_id: UUID | None = None

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    course_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    short_description: str | None = None
    description: str | None = None

    duration: str | None = Field(
        default=None,
        max_length=100,
    )

    level: str | None = Field(
        default=None,
        max_length=50,
    )

    is_published: bool | None = None
    display_order: int | None = None


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    thumbnail_url: str | None = Field(
        default=None,
        max_length=500,
    )

    created_at: datetime
    updated_at: datetime