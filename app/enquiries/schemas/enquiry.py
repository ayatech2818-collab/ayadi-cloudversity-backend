import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EnquiryType = Literal["contact", "enrollment"]
EnquiryStatus = Literal[
    "new",
    "contacted",
    "converted",
    "closed",
]


class EnquiryCreate(BaseModel):
    type: EnquiryType

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)

    date_of_birth: date | None = None

    email: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=30)

    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    zipcode: str | None = Field(default=None, max_length=20)

    message: str | None = None


class EnquiryUpdate(BaseModel):
    type: EnquiryType | None = None

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    date_of_birth: date | None = None

    email: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    zipcode: str | None = Field(default=None, max_length=20)

    message: str | None = None

    status: EnquiryStatus | None = None


class EnquiryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    type: EnquiryType

    first_name: str
    last_name: str | None

    date_of_birth: date | None

    email: str
    phone: str | None

    address: str | None
    city: str | None
    country: str | None
    zipcode: str | None

    message: str | None

    status: EnquiryStatus

    created_at: datetime
    updated_at: datetime