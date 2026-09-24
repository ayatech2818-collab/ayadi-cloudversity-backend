from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.core.database import get_db
from app.gallery.schemas.gallery_item import GalleryItemResponse
from app.gallery.services.gallery_item import create_gallery_items


router = APIRouter(
    prefix="/galleries",
    tags=["Gallery Items"],
)


@router.post(
    "/{gallery_id}/items",
    response_model=list[GalleryItemResponse],
    status_code=status.HTTP_201_CREATED,
)
def upload_gallery_items(
    gallery_id: UUID,
    files: Annotated[
        list[UploadFile],
        File(description="Select multiple images or videos"),
    ],
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return create_gallery_items(
        db=db,
        gallery_id=gallery_id,
        files=files,
    )