from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.core.database import get_db
from app.gallery.schemas.gallery import (
    GalleryCreate,
    GalleryResponse,
    GalleryUpdate,
)
from app.gallery.services.gallery import (
    create_gallery,
    get_galleries,
    get_gallery,
    update_gallery,
)


router = APIRouter(
    prefix="/galleries",
    tags=["Galleries"],
)


@router.post(
    "",
    response_model=GalleryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: GalleryCreate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return create_gallery(
        db=db,
        data=data,
        admin_id=admin.id,
    )


@router.get(
    "",
    response_model=list[GalleryResponse],
)
def list_galleries(
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_galleries(db)


@router.get(
    "/{gallery_id}",
    response_model=GalleryResponse,
)
def get(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_gallery(
        db=db,
        gallery_id=gallery_id,
    )


@router.patch(
    "/{gallery_id}",
    response_model=GalleryResponse,
)
def update(
    gallery_id: UUID,
    data: GalleryUpdate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return update_gallery(
        db=db,
        gallery_id=gallery_id,
        data=data,
    )