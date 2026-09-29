from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseSubcategoryBase(BaseModel):
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=150)
    slug: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    is_active: bool = True
    display_order: int = 0


class CourseSubcategoryCreate(CourseSubcategoryBase):
    pass


class CourseSubcategoryUpdate(BaseModel):
    category_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)
    slug: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class CourseSubcategoryResponse(CourseSubcategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime