from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from typing import Literal

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.blog.models.blog import BlogStatus
from app.blog.schemas.blog import (
    BlogCreate,
    BlogResponse,
    BlogUpdate,
)
from app.blog.services.blog import (
    create_blog,
    delete_blog,
    get_blog,
    get_blogs,
    update_blog,
    get_public_blog_by_slug
)
from app.core.database import get_db


router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
)


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(...),
    content: str = Form(...),

    cover_image: UploadFile | None = File(None),
    cover_image_alt: str | None = Form(None),

    category: str | None = Form(None),
    tags: str | None = Form(None),

    author_id: UUID | None = Form(None),

    status: BlogStatus = Form(BlogStatus.DRAFT),
    is_featured: bool = Form(False),

    published_at: datetime | None = Form(None),
    reading_time_minutes: int = Form(1),

    seo_title: str | None = Form(None),
    seo_description: str | None = Form(None),
    seo_keywords: str | None = Form(None),

    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    data = BlogCreate(
        title=title,
        slug=slug,
        excerpt=excerpt,
        content=content,
        cover_image_alt=cover_image_alt,
        category=category,
        tags=tags.split(",") if tags else None,
        author_id=author_id,
        status=status,
        is_featured=is_featured,
        published_at=published_at,
        reading_time_minutes=reading_time_minutes,
        seo_title=seo_title,
        seo_description=seo_description,
        seo_keywords=seo_keywords.split(",") if seo_keywords else None,
    )

    return create_blog(
        db=db,
        data=data,
        cover_image=cover_image,
        admin_id=admin.id,
    )


@router.get("", response_model=list[BlogResponse])
def list_blogs(
    search: str | None = None,
    status: Literal["draft", "published"] | None = None,
    category: str | None = None,
    sort_by: Literal[
        "newest",
        "oldest",
        "title-asc",
        "title-desc",
    ] = "newest",
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_blogs(
        db=db,
        search=search,
        status_filter=status,
        category=category,
        sort_by=sort_by,
    )

@router.get("/public", response_model=list[BlogResponse])
def list_public_blogs(
    search: str | None = None,
    category: str | None = None,
    sort_by: Literal[
        "newest",
        "oldest",
        "title-asc",
        "title-desc",
    ] = "newest",
    db: Session = Depends(get_db),
):
    return get_blogs(
        db=db,
        search=search,
        status_filter="published",
        category=category,
        sort_by=sort_by,
    )


@router.get("/public/{slug}", response_model=BlogResponse)
def get_public_blog(
    slug: str,
    db: Session = Depends(get_db),
):
    return get_public_blog_by_slug(
        db=db,
        slug=slug,
    )

@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
)
def get(
    blog_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_blog(
        db=db,
        blog_id=blog_id,
    )


@router.patch(
    "/{blog_id}",
    response_model=BlogResponse,
)
def update(
    blog_id: UUID,

    title: str | None = Form(None),
    slug: str | None = Form(None),
    excerpt: str | None = Form(None),
    content: str | None = Form(None),

    cover_image: UploadFile | None = File(None),
    cover_image_alt: str | None = Form(None),

    category: str | None = Form(None),
    tags: str | None = Form(None),

    author_id: UUID | None = Form(None),

    status: BlogStatus | None = Form(None),
    is_featured: bool | None = Form(None),

    published_at: datetime | None = Form(None),
    reading_time_minutes: int | None = Form(None),

    seo_title: str | None = Form(None),
    seo_description: str | None = Form(None),
    seo_keywords: str | None = Form(None),

    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    data = BlogUpdate(
        title=title,
        slug=slug,
        excerpt=excerpt,
        content=content,
        cover_image_alt=cover_image_alt,
        category=category,
        tags=tags.split(",") if tags else None,
        author_id=author_id,
        status=status,
        is_featured=is_featured,
        published_at=published_at,
        reading_time_minutes=reading_time_minutes,
        seo_title=seo_title,
        seo_description=seo_description,
        seo_keywords=seo_keywords.split(",") if seo_keywords else None,
    )

    return update_blog(
        db=db,
        blog_id=blog_id,
        data=data,
        cover_image=cover_image,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    blog_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_blog(
        db=db,
        blog_id=blog_id,
    )