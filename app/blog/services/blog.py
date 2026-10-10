from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from sqlalchemy import or_, select

from app.blog.models.blog import Blog,BlogStatus
from app.blog.schemas.blog import BlogCreate, BlogUpdate
from app.core.storage import delete_file, upload_image


def create_blog(
    db: Session,
    data: BlogCreate,
    cover_image: UploadFile | None,
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

    image_url = None
    image_key = None

    if cover_image:
        uploaded = upload_image(
            cover_image,
            folder="blogs",
        )

        image_url = uploaded["url"]
        image_key = uploaded["key"]

    blog_data = data.model_dump()

    blog_data["cover_image"] = image_url
    blog_data["cover_image_key"] = image_key

    blog = Blog(
        **blog_data,
        created_by=admin_id,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog




def get_blogs(
    db: Session,
    search: str | None = None,
    status_filter: str | None = None,
    category: str | None = None,
    sort_by: str = "newest",
) -> list[Blog]:

    query = select(Blog)

    # Search
    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            or_(
                Blog.title.ilike(search_term),
                Blog.excerpt.ilike(search_term),
                Blog.category.ilike(search_term),
            )
        )

    # Status
    if status_filter:
        query = query.where(
            Blog.status == status_filter
        )

    # Category
    if category:
        query = query.where(
            Blog.category == category
        )

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(
            Blog.created_at.asc()
        )
    elif sort_by == "title-asc":
        query = query.order_by(
            Blog.title.asc()
        )
    elif sort_by == "title-desc":
        query = query.order_by(
            Blog.title.desc()
        )
    else:
        query = query.order_by(
            Blog.created_at.desc()
        )

    result = db.scalars(query)

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
    cover_image: UploadFile | None,
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

    if cover_image:
        uploaded = upload_image(
            cover_image,
            folder="blogs",
        )

        blog.cover_image = uploaded["url"]
        blog.cover_image_key = uploaded["key"]

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

def get_public_blog_by_slug(
    db: Session,
    slug: str,
) -> Blog:
    blog = db.scalar(
        select(Blog).where(
            Blog.slug == slug,
            Blog.status == BlogStatus.PUBLISHED,
        )
    )

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found.",
        )

    return blog