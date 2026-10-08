from datetime import datetime, timedelta, timezone

from sqlalchemy import func, case, select
from sqlalchemy.orm import Session

from app.courses.models.course import Course
from app.blog.models.blog import Blog, BlogStatus
from app.enquiries.models.enquiry import Enquiry
from app.gallery.models.gallery import Gallery
from app.gallery.models.gallery_item import GalleryItem, GalleryMediaType

from .schemas import (
    DashboardSummaryResponse,
    DashboardCourseSummary,
    DashboardEnquirySummary,
    DashboardBlogSummary,
    DashboardGallerySummary,
    EnquiryAnalyticsResponse,
    EnquiryAnalyticsPoint,
    DashboardRecentEnquiriesResponse,
    DashboardRecentEnquiry,
)


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    # -------------------------
    # Courses
    # -------------------------
    course_counts = db.execute(
        select(
            func.count(Course.id).label("total"),
            func.count(
                case((Course.is_published.is_(True), 1))
            ).label("published"),
        )
    ).one()

    course_total = course_counts.total or 0
    course_published = course_counts.published or 0

    # -------------------------
    # Enquiries
    # -------------------------
    enquiry_counts = db.execute(
        select(
            func.count(Enquiry.id).label("total"),
            func.count(
                case((Enquiry.status == "new", 1))
            ).label("new"),
        )
    ).one()

    enquiry_total = enquiry_counts.total or 0
    enquiry_new = enquiry_counts.new or 0

    # -------------------------
    # Blogs
    # -------------------------
    blog_counts = db.execute(
        select(
            func.count(Blog.id).label("total"),
            func.count(
                case((Blog.status == BlogStatus.PUBLISHED, 1))
            ).label("published"),
        )
    ).one()

    blog_total = blog_counts.total or 0
    blog_published = blog_counts.published or 0

    # -------------------------
    # Gallery
    # -------------------------
    gallery_total = db.scalar(
        select(func.count(Gallery.id))
    ) or 0

    image_count = db.scalar(
        select(func.count(GalleryItem.id)).where(
            GalleryItem.media_type == GalleryMediaType.IMAGE
        )
    ) or 0

    video_count = db.scalar(
        select(func.count(GalleryItem.id)).where(
            GalleryItem.media_type == GalleryMediaType.VIDEO
        )
    ) or 0

    return DashboardSummaryResponse(
        courses=DashboardCourseSummary(
            total=course_total,
            published=course_published,
            draft=course_total - course_published,
        ),
        enquiries=DashboardEnquirySummary(
            total=enquiry_total,
            new=enquiry_new,
        ),
        blogs=DashboardBlogSummary(
            total=blog_total,
            published=blog_published,
            draft=blog_total - blog_published,
        ),
        gallery=DashboardGallerySummary(
            total=gallery_total,
            images=image_count,
            videos=video_count,
        ),
    )

def get_enquiry_analytics(
    db: Session,
    days: int,
) -> EnquiryAnalyticsResponse:
    if days not in (7, 30, 90):
        raise ValueError("days must be 7, 30, or 90")

    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days - 1)

    rows = db.execute(
        select(
            func.date(Enquiry.created_at).label("date"),
            func.count(
                case((Enquiry.type == "enrollment", 1))
            ).label("enrollment"),
            func.count(
                case((Enquiry.type == "contact", 1))
            ).label("contact"),
        )
        .where(Enquiry.created_at >= start_date)
        .group_by(func.date(Enquiry.created_at))
        .order_by(func.date(Enquiry.created_at))
    ).all()

    row_map = {
        row.date: {
            "enrollment": row.enrollment or 0,
            "contact": row.contact or 0,
        }
        for row in rows
    }

    data = []

    for index in range(days):
        current_date = (
            start_date.date() + timedelta(days=index)
        )

        values = row_map.get(
            current_date,
            {
                "enrollment": 0,
                "contact": 0,
            },
        )

        data.append(
            EnquiryAnalyticsPoint(
                date=current_date,
                enrollment=values["enrollment"],
                contact=values["contact"],
            )
        )

    enrollment_total = sum(
        point.enrollment for point in data
    )

    contact_total = sum(
        point.contact for point in data
    )

    return EnquiryAnalyticsResponse(
        days=days,
        total=enrollment_total + contact_total,
        enrollment=enrollment_total,
        contact=contact_total,
        data=data,
    )

def get_recent_enquiries(
    db: Session,
    limit: int = 7,
) -> DashboardRecentEnquiriesResponse:
    enquiries = db.scalars(
        select(Enquiry)
        .order_by(Enquiry.created_at.desc())
        .limit(limit)
    ).all()

    return DashboardRecentEnquiriesResponse(
        items=[
            DashboardRecentEnquiry.model_validate(enquiry)
            for enquiry in enquiries
        ]
    )