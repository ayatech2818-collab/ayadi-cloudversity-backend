import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.courses.models.course_brand import CourseBrand
    from app.courses.models.course_category import CourseCategory
    from app.courses.models.course_subcategory import CourseSubcategory


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_brands.id"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_categories.id"),
        nullable=True,
        index=True,
    )

    subcategory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_subcategories.id"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
    )

    course_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    short_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    thumbnail_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    duration: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    brand: Mapped["CourseBrand"] = relationship(
        "CourseBrand",
        back_populates="courses",
    )

    category: Mapped["CourseCategory"] = relationship(
        "CourseCategory",
        back_populates="courses",
    )

    subcategory: Mapped["CourseSubcategory"] = relationship(
        "CourseSubcategory",
        back_populates="courses",
    )