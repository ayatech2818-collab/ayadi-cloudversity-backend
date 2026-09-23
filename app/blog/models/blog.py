import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BlogStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    excerpt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    cover_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    cover_image_alt: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    # Publicly displayed author
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("blog_authors.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Admin who created the blog
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admin_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[BlogStatus] = mapped_column(
        Enum(BlogStatus, name="blog_status"),
        default=BlogStatus.DRAFT,
        nullable=False,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reading_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    seo_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    seo_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    seo_keywords: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
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