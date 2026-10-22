
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_admin
from app.feedback.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackApproval,
)
from app.feedback.services.feedback_service import (
    create_feedback as create_feedback_service,
    get_approved_feedback,
    get_all_feedback,
    update_feedback_approval,
)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


# Public: Submit feedback
@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_feedback_route(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
):
    return create_feedback_service(
        db=db,
        data=data,
    )


# Public: Get approved feedback only
@router.get(
    "",
    response_model=list[FeedbackResponse],
)
def get_public_feedback(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_approved_feedback(
        db=db,
        skip=skip,
        limit=limit,
    )


# Admin: Get all feedback
@router.get(
    "/admin",
    response_model=list[FeedbackResponse],
)
def get_admin_feedback(
    is_approved: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return get_all_feedback(
        db=db,
        is_approved=is_approved,
        skip=skip,
        limit=limit,
    )


# Admin: Approve or reject feedback
@router.patch(
    "/admin/{feedback_id}/approval",
    response_model=FeedbackResponse,
)
def approve_feedback(
    feedback_id: uuid.UUID,
    data: FeedbackApproval,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return update_feedback_approval(
        db=db,
        feedback_id=feedback_id,
        data=data,
    )
