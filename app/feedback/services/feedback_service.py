
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feedback.models.feedback import Feedback
from app.feedback.schemas.feedback import FeedbackCreate, FeedbackApproval


def create_feedback(
    db: Session,
    data: FeedbackCreate,
) -> Feedback:

    feedback = Feedback(
        **data.model_dump(),
        is_approved=False,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback


def get_approved_feedback(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Feedback]:

    query = (
        select(Feedback)
        .where(Feedback.is_approved.is_(True))
        .order_by(Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = db.scalars(query)

    return list(result.all())


def get_all_feedback(
    db: Session,
    is_approved: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Feedback]:

    query = select(Feedback)

    if is_approved is not None:
        query = query.where(
            Feedback.is_approved == is_approved
        )

    query = (
        query
        .order_by(Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = db.scalars(query)

    return list(result.all())


def get_feedback(
    db: Session,
    feedback_id: uuid.UUID,
) -> Feedback:

    feedback = db.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found.",
        )

    return feedback


def update_feedback_approval(
    db: Session,
    feedback_id: uuid.UUID,
    data: FeedbackApproval,
) -> Feedback:

    feedback = get_feedback(
        db=db,
        feedback_id=feedback_id,
    )

    feedback.is_approved = data.is_approved

    db.commit()
    db.refresh(feedback)

    return feedback
