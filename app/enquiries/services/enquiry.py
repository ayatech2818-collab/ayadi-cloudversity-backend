from uuid import UUID

from fastapi import HTTPException, status
from io import BytesIO
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
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


def export_enquiries(
    db: Session,
    status_filter: str | None = None,
) -> BytesIO:

    query = select(Enquiry)

    # Filter by status when provided
    if status_filter:
        query = query.where(
            Enquiry.status == status_filter
        )

    # Export oldest to newest
    query = query.order_by(
        Enquiry.created_at.asc()
    )

    enquiries = list(db.scalars(query).all())

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Enquiries"

    headers = [
        "Sl. No.",
        "Submitted Date",
        "Enquiry Type",
        "Status",
        "First Name",
        "Last Name",
        "Full Name",
        "Email",
        "Phone",
        "DOB",
        "City",
        "Country",
        "Zipcode",
        "Address",
        "Interested Course",
        "Message",
    ]

    worksheet.append(headers)

    # Header styling
    for cell in worksheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="15803D",
            end_color="15803D",
            fill_type="solid",
        )
        cell.alignment = Alignment(horizontal="center")

    for index, enquiry in enumerate(enquiries, start=1):

        message = enquiry.message or ""
        course_title = enquiry.course_title or ""

        # Extract legacy course information from message
        if not course_title:
            import re

            match = re.match(
                r"^Course:\s*(.*?)\s*\(ID:\s*[^)]+\)\s*\n?",
                message,
                re.IGNORECASE,
            )

            if match:
                course_title = match.group(1).strip()
                message = message[match.end():]

        full_name = " ".join(
            filter(
                None,
                [enquiry.first_name, enquiry.last_name],
            )
        )

        row = [
            index,
            enquiry.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if enquiry.created_at else "",
            enquiry.type,
            enquiry.status,
            enquiry.first_name,
            enquiry.last_name or "",
            full_name,
            enquiry.email,
            enquiry.phone or "",
            enquiry.date_of_birth.strftime("%Y-%m-%d")
            if enquiry.date_of_birth else "",
            enquiry.city or "",
            enquiry.country or "",
            enquiry.zipcode or "",
            enquiry.address or "",
            course_title,
            message,
        ]

        # Prevent Excel formula injection.
        safe_row = [
            "'" + value
            if isinstance(value, str)
            and value.startswith(("=", "+", "-", "@"))
            else value
            for value in row
        ]

        worksheet.append(safe_row)

    # Column widths
    column_widths = {
        "A": 10,
        "B": 22,
        "C": 16,
        "D": 16,
        "E": 18,
        "F": 18,
        "G": 25,
        "H": 30,
        "I": 18,
        "J": 15,
        "K": 18,
        "L": 18,
        "M": 14,
        "N": 30,
        "O": 30,
        "P": 70,
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    # Return workbook in memory
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


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