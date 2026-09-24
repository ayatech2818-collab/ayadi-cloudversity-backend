import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.blog.models.blog import BlogStatus


class BlogCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    excerpt: str
    content: str

    cover_image: str | None = None
    cover_image_key: str | None = Field(default=None, max_length=500)
    cover_image_alt: str | None = Field(default=None, max_length=255)

    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None

    author_id: uuid.UUID | None = None

    status: BlogStatus = BlogStatus.DRAFT
    is_featured: bool = False

    published_at: datetime | None = None
    reading_time_minutes: int = Field(default=1, ge=1)

    seo_title: str | None = Field(default=None, max_length=255)
    seo_description: str | None = None
    seo_keywords: list[str] | None = None


class BlogUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    excerpt: str | None = None
    content: str | None = None

    cover_image: str | None = None
    cover_image_key: str | None = Field(default=None, max_length=500)
    cover_image_alt: str | None = Field(default=None, max_length=255)

    category: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None

    author_id: uuid.UUID | None = None

    status: BlogStatus | None = None
    is_featured: bool | None = None

    published_at: datetime | None = None
    reading_time_minutes: int | None = Field(default=None, ge=1)

    seo_title: str | None = Field(default=None, max_length=255)
    seo_description: str | None = None
    seo_keywords: list[str] | None = None


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    excerpt: str
    content: str

    cover_image: str | None
    cover_image_alt: str | None

    category: str | None
    tags: list[str] | None

    author_id: uuid.UUID | None
    created_by: uuid.UUID | None

    status: BlogStatus
    is_featured: bool

    published_at: datetime | None
    reading_time_minutes: int

    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str] | None

    created_at: datetime
    updated_at: datetime