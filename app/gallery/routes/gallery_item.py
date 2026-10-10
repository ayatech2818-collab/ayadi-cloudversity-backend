
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status, Form, Query
from sqlalchemy.orm import Session
from app.gallery.models.gallery_item import GalleryMediaType
from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.core.database import get_db
from app.gallery.schemas.gallery_item import (
    GalleryItemResponse,
    GalleryItemUpdate,
)
from app.gallery.services.gallery_item import (
    create_gallery_items,
    delete_gallery_item,
    get_gallery_item,
    get_gallery_items,
    update_gallery_item,
)


router = APIRouter(
    prefix="/galleries",
    tags=["Gallery Items"],
)


@router.get(
    "/public/{gallery_id}/items",
    response_model=list[GalleryItemResponse],
)
def list_gallery_items_public(
    gallery_id: UUID,
    media_type: GalleryMediaType | None = Query(
        default=None,
        description="Filter by media type",
    ),
    db: Session = Depends(get_db),
):
    return get_gallery_items(
        db=db,
        gallery_id=gallery_id,
        media_type=media_type,
        public_only=True,
    )

@router.get(
    "/public/{gallery_id}/items/{item_id}",
    response_model=GalleryItemResponse,
)
def get_item_public(
    gallery_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
):
    return get_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
        public_only=True,
    )

@router.post(
    "/{gallery_id}/items",
    response_model=list[GalleryItemResponse],
    status_code=status.HTTP_201_CREATED,
)
def upload_gallery_items(
    gallery_id: UUID,
    files: list[UploadFile] = File(
        ...,
        description="Select multiple images or videos",
    ),
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return create_gallery_items(
        db=db,
        gallery_id=gallery_id,
        files=files,
    )


@router.get(
    "/{gallery_id}/items",
    response_model=list[GalleryItemResponse],
)
def list_gallery_items(
    gallery_id: UUID,
    media_type: GalleryMediaType | None = Query(
        default=None,
        description="Filter by media type",
    ),
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_gallery_items(
        db=db,
        gallery_id=gallery_id,
        media_type=media_type,
    )


@router.get(
    "/{gallery_id}/items/{item_id}",
    response_model=GalleryItemResponse,
)
def get_item(
    gallery_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
    )


@router.patch(
    "/{gallery_id}/items/{item_id}",
    response_model=GalleryItemResponse,
)
def update_item(
    gallery_id: UUID,
    item_id: UUID,
    file: UploadFile | None = File(
        default=None,
        description="Optional replacement image or video",
    ),
    alt_text: str | None = Form(
        default=None,
    ),
    display_order: int | None = Form(
        default=None,
        ge=0,
    ),
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return update_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
        file=file,
        alt_text=alt_text,
        display_order=display_order,
    )


@router.delete(
    "/{gallery_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    gallery_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_gallery_item(
        db=db,
        gallery_id=gallery_id,
        item_id=item_id,
    )