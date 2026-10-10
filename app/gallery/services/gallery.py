from uuid import UUID
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.gallery.models.gallery import Gallery
from app.gallery.schemas.gallery import GalleryCreate, GalleryUpdate
from app.core.storage import delete_file
from app.gallery.models.gallery_item import GalleryItem


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
    search: str | None = None,
    is_published: bool | None = None,
    event_date_from: date | None = None,
    event_date_to: date | None = None,
) -> list[Gallery]:

    query = select(Gallery)

    if search:
        search_pattern = f"%{search.strip()}%"

        query = query.where(
            or_(
                Gallery.title.ilike(search_pattern),
                Gallery.slug.ilike(search_pattern),
            )
        )

    if is_published is not None:
        query = query.where(
            Gallery.is_published == is_published
        )

    if event_date_from is not None:
        query = query.where(
            Gallery.event_date >= event_date_from
        )

    if event_date_to is not None:
        query = query.where(
            Gallery.event_date <= event_date_to
        )

    query = query.order_by(
        Gallery.event_date.desc().nullslast()
    )

    galleries = list(db.scalars(query).all())

    if not galleries:
        return []

    gallery_ids = [gallery.id for gallery in galleries]

    items = db.scalars(
        select(GalleryItem)
        .where(GalleryItem.gallery_id.in_(gallery_ids))
        .order_by(GalleryItem.display_order.asc())
    ).all()

    items_by_gallery: dict[UUID, list[GalleryItem]] = {}

    for item in items:
        items_by_gallery.setdefault(
            item.gallery_id,
            [],
        ).append(item)

    for gallery in galleries:
        gallery.items = items_by_gallery.get(
            gallery.id,
            [],
        )

    return galleries

def get_gallery(
    db: Session,
    gallery_id: UUID,
    public_only: bool = False,
) -> Gallery:
    gallery = db.get(Gallery, gallery_id)

    if not gallery or (public_only and not gallery.is_published):
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

def delete_gallery(
    db: Session,
    gallery_id: UUID,
) -> None:

    gallery = get_gallery(
        db=db,
        gallery_id=gallery_id,
    )

    items = db.scalars(
        select(GalleryItem).where(
            GalleryItem.gallery_id == gallery_id
        )
    ).all()

    storage_keys = [
        item.storage_key
        for item in items
        if item.storage_key
    ]

    try:
        for storage_key in storage_keys:
            delete_file(storage_key)

        db.delete(gallery)
        db.commit()

    except Exception:
        db.rollback()
        raise