from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.blog.models.author import BlogAuthor
from app.blog.schemas.author import AuthorCreate, AuthorUpdate
from app.core.storage import delete_file


def create_author(db: Session, data: AuthorCreate) -> BlogAuthor:
    author = BlogAuthor(**data.model_dump())

    db.add(author)
    db.commit()
    db.refresh(author)

    return author


def get_authors(db: Session) -> list[BlogAuthor]:
    result = db.scalars(
        select(BlogAuthor)
        .where(BlogAuthor.is_active.is_(True))
        .order_by(BlogAuthor.name.asc())
    )

    return list(result.all())


def get_author(db: Session, author_id: UUID) -> BlogAuthor:
    author = db.get(BlogAuthor, author_id)

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found.",
        )

    return author


def update_author(
    db: Session,
    author_id: UUID,
    data: AuthorUpdate,
) -> BlogAuthor:
    author = get_author(db, author_id)

    update_data = data.model_dump(exclude_unset=True)

    old_profile_image_key = author.profile_image_key

    for field, value in update_data.items():
        setattr(author, field, value)

    db.commit()
    db.refresh(author)

    new_profile_image_key = author.profile_image_key

    if (
    old_profile_image_key
    and old_profile_image_key != new_profile_image_key
    ):
        delete_file(old_profile_image_key)

    return author


def delete_author(db: Session, author_id: UUID) -> None:
    author = get_author(db, author_id)

    author.is_active = False

    db.commit()


def restore_author(
    db: Session,
    author_id: UUID,
) -> BlogAuthor:
    author = get_author(db, author_id)

    author.is_active = True

    db.commit()
    db.refresh(author)

    return author