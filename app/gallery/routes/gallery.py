from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query
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
    delete_gallery,
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
    search: str | None = Query(
        default=None,
        description="Search by gallery title or slug",
    ),
    is_published: bool | None = Query(
        default=None,
        description="Filter by published status",
    ),
    event_date_from: date | None = Query(
        default=None,
        description="Filter galleries from this date",
    ),
    event_date_to: date | None = Query(
        default=None,
        description="Filter galleries up to this date",
    ),
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_galleries(
        db=db,
        search=search,
        is_published=is_published,
        event_date_from=event_date_from,
        event_date_to=event_date_to,
    )


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

@router.delete(
    "/{gallery_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    gallery_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_gallery(
        db=db,
        gallery_id=gallery_id,
    )