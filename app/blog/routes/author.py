from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.blog.schemas.author import (
    AuthorCreate,
    AuthorResponse,
    AuthorUpdate,
)
from app.blog.services.author import (
    create_author,
    delete_author,
    get_author,
    get_authors,
    update_author,
    restore_author,
)
from app.core.database import get_db


router = APIRouter(
    prefix="/blog-authors",
    tags=["Blog Authors"],
)


@router.post(
    "",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: AuthorCreate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return create_author(
        db=db,
        data=data,
    )


@router.get(
    "",
    response_model=list[AuthorResponse],
)
def list_authors(
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_authors(db)


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
)
def get(
    author_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_author(
        db=db,
        author_id=author_id,
    )


@router.patch(
    "/{author_id}",
    response_model=AuthorResponse,
)
def update(
    author_id: UUID,
    data: AuthorUpdate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return update_author(
        db=db,
        author_id=author_id,
        data=data,
    )


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    author_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_author(
        db=db,
        author_id=author_id,
    )

@router.patch(
    "/{author_id}/restore",
    response_model=AuthorResponse,
)
def restore(
    author_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return restore_author(
        db=db,
        author_id=author_id,
    )