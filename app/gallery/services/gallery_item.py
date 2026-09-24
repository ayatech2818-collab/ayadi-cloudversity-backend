from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.storage import upload_gallery_file
from app.gallery.models.gallery import Gallery
from app.gallery.models.gallery_item import GalleryItem


def create_gallery_items(
    db: Session,
    gallery_id: UUID,
    files: list[UploadFile],
) -> list[GalleryItem]:
    gallery = db.get(Gallery, gallery_id)

    if not gallery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery not found.",
        )

    max_order = db.scalar(
        select(func.max(GalleryItem.display_order))
        .where(GalleryItem.gallery_id == gallery_id)
    )

    next_order = (max_order + 1) if max_order is not None else 0

    items = []

    for file in files:
        upload_result = upload_gallery_file(
            file=file,
            gallery_id=str(gallery_id),
        )

        item = GalleryItem(
            gallery_id=gallery_id,
            file_name=upload_result["file_name"],
            storage_key=upload_result["key"],
            file_url=upload_result["url"],
            media_type=upload_result["media_type"],
            mime_type=upload_result["mime_type"],
            file_size=upload_result["file_size"],
            display_order=next_order,
        )

        db.add(item)
        items.append(item)

        next_order += 1

    db.commit()

    for item in items:
        db.refresh(item)

    return items