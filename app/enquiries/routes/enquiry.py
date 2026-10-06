from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.core.database import get_db

from app.enquiries.schemas.enquiry import (
    EnquiryCreate,
    EnquiryResponse,
    EnquiryUpdate,
)

from app.enquiries.services.enquiry import (
    create_enquiry,
    delete_enquiry,
    get_enquiries,
    get_enquiry,
    update_enquiry,
)


router = APIRouter(
    prefix="/enquiries",
    tags=["Enquiries"],
)


@router.post(
    "",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: EnquiryCreate,
    db: Session = Depends(get_db),
):
    return create_enquiry(
        db=db,
        data=data,
    )


@router.get(
    "",
    response_model=list[EnquiryResponse],
)
def list_enquiries(
    search: str | None = None,
    type: Literal["contact", "enrollment"] | None = None,
    status: Literal[
        "new",
        "contacted",
        "converted",
        "closed",
    ] | None = None,
    sort_by: Literal[
        "newest",
        "oldest",
        "name-asc",
        "name-desc",
    ] = "newest",
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_enquiries(
        db=db,
        search=search,
        type_filter=type,
        status_filter=status,
        sort_by=sort_by,
    )


@router.get(
    "/{enquiry_id}",
    response_model=EnquiryResponse,
)
def get(
    enquiry_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_enquiry(
        db=db,
        enquiry_id=enquiry_id,
    )


@router.patch(
    "/{enquiry_id}",
    response_model=EnquiryResponse,
)
def update(
    enquiry_id: UUID,
    data: EnquiryUpdate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return update_enquiry(
        db=db,
        enquiry_id=enquiry_id,
        data=data,
    )


@router.delete(
    "/{enquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    enquiry_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_enquiry(
        db=db,
        enquiry_id=enquiry_id,
    )