from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.enquiries.models.enquiry import Enquiry
from app.enquiries.schemas.enquiry import (
    EnquiryCreate,
    EnquiryUpdate,
)


def create_enquiry(
    db: Session,
    data: EnquiryCreate,
) -> Enquiry:

    enquiry = Enquiry(
        **data.model_dump(),
        status="new",
    )

    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    return enquiry


def get_enquiries(
    db: Session,
    search: str | None = None,
    type_filter: str | None = None,
    status_filter: str | None = None,
    sort_by: str = "newest",
) -> list[Enquiry]:

    query = select(Enquiry)

    # Search
    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            or_(
                Enquiry.first_name.ilike(search_term),
                Enquiry.last_name.ilike(search_term),
                Enquiry.email.ilike(search_term),
                Enquiry.phone.ilike(search_term),
                Enquiry.city.ilike(search_term),
                Enquiry.country.ilike(search_term),
            )
        )

    # Type
    if type_filter:
        query = query.where(
            Enquiry.type == type_filter
        )

    # Status
    if status_filter:
        query = query.where(
            Enquiry.status == status_filter
        )

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(
            Enquiry.created_at.asc()
        )
    elif sort_by == "name-asc":
        query = query.order_by(
            Enquiry.first_name.asc(),
            Enquiry.last_name.asc(),
        )
    elif sort_by == "name-desc":
        query = query.order_by(
            Enquiry.first_name.desc(),
            Enquiry.last_name.desc(),
        )
    else:
        query = query.order_by(
            Enquiry.created_at.desc()
        )

    result = db.scalars(query)

    return list(result.all())


def get_enquiry(
    db: Session,
    enquiry_id: UUID,
) -> Enquiry:

    enquiry = db.get(Enquiry, enquiry_id)

    if not enquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found.",
        )

    return enquiry


def update_enquiry(
    db: Session,
    enquiry_id: UUID,
    data: EnquiryUpdate,
) -> Enquiry:

    enquiry = get_enquiry(
        db=db,
        enquiry_id=enquiry_id,
    )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(enquiry, field, value)

    db.commit()
    db.refresh(enquiry)

    return enquiry


def delete_enquiry(
    db: Session,
    enquiry_id: UUID,
) -> None:

    enquiry = get_enquiry(
        db=db,
        enquiry_id=enquiry_id,
    )

    db.delete(enquiry)
    db.commit()