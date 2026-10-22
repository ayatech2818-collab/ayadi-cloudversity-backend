
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


FeedbackName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=150),
]

FeedbackMessage = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=5, max_length=3000),
]


class FeedbackCreate(BaseModel):
    name: FeedbackName
    rating: int = Field(ge=1, le=5)
    message: FeedbackMessage


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    name: str
    rating: int
    message: str
    is_approved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackApproval(BaseModel):
    is_approved: bool
