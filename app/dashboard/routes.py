from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_admin

from .schemas import (
    DashboardSummaryResponse,
    EnquiryAnalyticsResponse,
    DashboardRecentEnquiriesResponse,
)
from .service import (
    get_dashboard_summary,
    get_enquiry_analytics,
    get_recent_enquiries,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return get_dashboard_summary(db)


@router.get(
    "/enquiries/analytics",
    response_model=EnquiryAnalyticsResponse,
)
def dashboard_enquiry_analytics(
    days: int = Query(
        default=7,
        description="Analytics range. Supported values: 7, 30, 90",
    ),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    try:
        return get_enquiry_analytics(db, days)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/enquiries/recent",
    response_model=DashboardRecentEnquiriesResponse,
)
def dashboard_recent_enquiries(
    limit: int = Query(default=7, ge=1, le=50),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    return get_recent_enquiries(
        db=db,
        limit=limit,
    )