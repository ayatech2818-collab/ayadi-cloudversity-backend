from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.blog.models.blog import Blog
from app.blog.schemas.blog import BlogCreate, BlogUpdate
from app.core.storage import delete_file


def create_blog(
    db: Session,
    data: BlogCreate,
    admin_id: UUID,
) -> Blog:

    existing_blog = db.scalar(
        select(Blog).where(Blog.slug == data.slug)
    )

    if existing_blog:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A blog with this slug already exists.",
        )

    blog = Blog(
        **data.model_dump(),
        created_by=admin_id,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog


def get_blogs(
    db: Session,
) -> list[Blog]:

    result = db.scalars(
        select(Blog).order_by(Blog.created_at.desc())
    )

    return list(result.all())


def get_blog(
    db: Session,
    blog_id: UUID,
) -> Blog:

    blog = db.get(Blog, blog_id)

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found.",
        )

    return blog


def update_blog(
    db: Session,
    blog_id: UUID,
    data: BlogUpdate,
) -> Blog:
    blog = get_blog(db, blog_id)

    update_data = data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != blog.slug:

        existing_blog = db.scalar(
            select(Blog).where(
                Blog.slug == update_data["slug"],
                Blog.id != blog_id,
            )
        )

        if existing_blog:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A blog with this slug already exists.",
            )

    old_cover_image_key = blog.cover_image_key

    for field, value in update_data.items():
        setattr(blog, field, value)

    db.commit()
    db.refresh(blog)

    new_cover_image_key = blog.cover_image_key

    if (
        old_cover_image_key
        and old_cover_image_key != new_cover_image_key
    ):
        delete_file(old_cover_image_key)

    return blog


def delete_blog(
    db: Session,
    blog_id: UUID,
) -> None:
    blog = get_blog(db, blog_id)

    old_cover_image_key = blog.cover_image_key

    db.delete(blog)
    db.commit()

    if old_cover_image_key:
        delete_file(old_cover_image_key)