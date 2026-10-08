import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class DashboardCourseSummary(BaseModel):
    total: int
    published: int
    draft: int


class DashboardEnquirySummary(BaseModel):
    total: int
    new: int


class DashboardBlogSummary(BaseModel):
    total: int
    published: int
    draft: int


class DashboardGallerySummary(BaseModel):
    total: int
    images: int
    videos: int


class DashboardSummaryResponse(BaseModel):
    courses: DashboardCourseSummary
    enquiries: DashboardEnquirySummary
    blogs: DashboardBlogSummary
    gallery: DashboardGallerySummary


class EnquiryAnalyticsPoint(BaseModel):
    date: date
    enrollment: int
    contact: int


class EnquiryAnalyticsResponse(BaseModel):
    days: Literal[7, 30, 90]
    total: int
    enrollment: int
    contact: int
    data: list[EnquiryAnalyticsPoint]


class DashboardRecentEnquiry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    first_name: str
    last_name: str | None
    email: str
    status: str
    created_at: datetime


class DashboardRecentEnquiriesResponse(BaseModel):
    items: list[DashboardRecentEnquiry]