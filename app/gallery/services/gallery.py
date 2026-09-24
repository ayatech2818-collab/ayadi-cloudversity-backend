from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.gallery.models.gallery import Gallery
from app.gallery.schemas.gallery import GalleryCreate, GalleryUpdate


def create_gallery(
    db: Session,
    data: GalleryCreate,
    admin_id: UUID,
) -> Gallery:
    existing_gallery = db.scalar(
        select(Gallery).where(Gallery.slug == data.slug)
    )

    if existing_gallery:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A gallery with this slug already exists.",
        )

    gallery = Gallery(
        **data.model_dump(),
        created_by=admin_id,
    )

    db.add(gallery)
    db.commit()
    db.refresh(gallery)

    return gallery


def get_galleries(
    db: Session,
) -> list[Gallery]:
    result = db.scalars(
        select(Gallery)
        .order_by(Gallery.event_date.desc().nullslast())
    )

    return list(result.all())


def get_gallery(
    db: Session,
    gallery_id: UUID,
) -> Gallery:
    gallery = db.get(Gallery, gallery_id)

    if not gallery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery not found.",
        )

    return gallery


def update_gallery(
    db: Session,
    gallery_id: UUID,
    data: GalleryUpdate,
) -> Gallery:
    gallery = get_gallery(db, gallery_id)

    update_data = data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != gallery.slug:
        existing_gallery = db.scalar(
            select(Gallery).where(
                Gallery.slug == update_data["slug"],
                Gallery.id != gallery_id,
            )
        )

        if existing_gallery:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A gallery with this slug already exists.",
            )

    for field, value in update_data.items():
        setattr(gallery, field, value)

    db.commit()
    db.refresh(gallery)

    return gallery