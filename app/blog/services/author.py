from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import HTTPException, UploadFile
from app.core.storage import delete_file, upload_image

from app.blog.models.author import BlogAuthor
from app.blog.schemas.author import AuthorCreate, AuthorUpdate
from app.core.storage import delete_file


def create_author(
    db: Session,
    name: str,
    designation: str | None,
    bio: str | None,
    linkedin_url: str | None,
    profile_image: UploadFile | None,
) -> BlogAuthor:

    image_url = None
    image_key = None

    if profile_image:
        uploaded = upload_image(
            profile_image,
            folder="authors",
        )

        image_url = uploaded["url"]
        image_key = uploaded["key"]

    author = BlogAuthor(
        name=name,
        designation=designation,
        bio=bio,
        linkedin_url=linkedin_url,
        profile_image=image_url,
        profile_image_key=image_key,
    )

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
    name: str | None,
    designation: str | None,
    bio: str | None,
    linkedin_url: str | None,
    profile_image: UploadFile | None,
) -> BlogAuthor:

    author = get_author(db, author_id)

    old_profile_image_key = author.profile_image_key

    if name is not None:
        author.name = name

    if designation is not None:
        author.designation = designation

    if bio is not None:
        author.bio = bio

    if linkedin_url is not None:
        author.linkedin_url = linkedin_url

    if profile_image:
        uploaded = upload_image(
            profile_image,
            folder="authors",
        )

        author.profile_image = uploaded["url"]
        author.profile_image_key = uploaded["key"]

    db.commit()
    db.refresh(author)

    if (
        old_profile_image_key
        and old_profile_image_key != author.profile_image_key
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

def get_deleted_authors(
    db: Session,
) -> list[BlogAuthor]:
    result = db.scalars(
        select(BlogAuthor)
        .where(BlogAuthor.is_active.is_(False))
        .order_by(BlogAuthor.name.asc())
    )

    return list(result.all())