from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.gallery.models.gallery import Gallery
from app.gallery.models.gallery_item import GalleryItem, GalleryMediaType
from app.core.storage import delete_file, upload_gallery_file


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

    items: list[GalleryItem] = []
    uploaded_keys: list[str] = []

    try:
        for index, file in enumerate(files):
            uploaded = upload_gallery_file(
                file=file,
                gallery_id=str(gallery_id),
            )

            uploaded_keys.append(uploaded["key"])

            item = GalleryItem(
                gallery_id=gallery_id,
                file_name=uploaded["file_name"],
                storage_key=uploaded["key"],
                file_url=uploaded["url"],
                media_type=uploaded["media_type"],
                mime_type=uploaded["mime_type"],
                file_size=uploaded["file_size"],
                display_order=index,
            )

            db.add(item)
            items.append(item)

        db.commit()

        for item in items:
            db.refresh(item)

        return items

    except Exception:
        db.rollback()

        for key in uploaded_keys:
            try:
                delete_file(key)
            except Exception:
                pass

        raise


def get_gallery_items(
    db: Session,
    gallery_id: UUID,
    media_type: GalleryMediaType | None = None,
    public_only: bool = False,
) -> list[GalleryItem]:

    gallery = db.get(Gallery, gallery_id)

    if not gallery or (public_only and not gallery.is_published):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery not found.",
        )

    query = (
        select(GalleryItem)
        .where(GalleryItem.gallery_id == gallery_id)
    )

    if media_type is not None:
        query = query.where(
            GalleryItem.media_type == media_type
        )

    query = query.order_by(
        GalleryItem.display_order.asc()
    )

    result = db.scalars(query)

    return list(result.all())


def get_gallery_item(
    db: Session,
    gallery_id: UUID,
    item_id: UUID,
    public_only: bool = False,
) -> GalleryItem:


    gallery = db.get(Gallery, gallery_id)

    if not gallery or (public_only and not gallery.is_published):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery not found.",
        )
        
    item = db.scalar(
        select(GalleryItem).where(
            GalleryItem.id == item_id,
            GalleryItem.gallery_id == gallery_id,
        )
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery item not found.",
        )

    return item


def update_gallery_item(
    db: Session,
    gallery_id: UUID,
    item_id: UUID,
    file: UploadFile | None = None,
    alt_text: str | None = None,
    display_order: int | None = None,
) -> GalleryItem:

    item = get_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
    )

    old_storage_key = None
    new_storage_key = None

    try:
        # Replace image/video if a new file was provided
        if file is not None:
            uploaded = upload_gallery_file(
                file=file,
                gallery_id=str(gallery_id),
            )

            new_storage_key = uploaded["key"]
            old_storage_key = item.storage_key

            item.file_name = uploaded["file_name"]
            item.storage_key = uploaded["key"]
            item.file_url = uploaded["url"]
            item.media_type = uploaded["media_type"]
            item.mime_type = uploaded["mime_type"]
            item.file_size = uploaded["file_size"]

        if alt_text is not None:
            item.alt_text = alt_text

        if display_order is not None:
            item.display_order = display_order

        db.commit()
        db.refresh(item)

    except Exception:
        db.rollback()

        # If new file was uploaded but DB update failed,
        # remove the newly uploaded file.
        if new_storage_key:
            try:
                delete_file(new_storage_key)
            except Exception:
                pass

        raise

    # Delete old S3 file only after DB update succeeds
    if old_storage_key:
        try:
            delete_file(old_storage_key)
        except Exception:
            # DB is already updated, so don't make the API
            # report failure just because old storage cleanup failed.
            pass

    return item


def delete_gallery_item(
    db: Session,
    gallery_id: UUID,
    item_id: UUID,
) -> None:
    item = get_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
    )

    try:
        # Delete media from S3
        delete_file(item.storage_key)

        # Delete database record
        db.delete(item)
        db.commit()

    except Exception:
        db.rollback()
        raise