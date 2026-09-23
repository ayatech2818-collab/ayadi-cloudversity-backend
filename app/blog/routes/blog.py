from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.blog.schemas.blog import (
    BlogCreate,
    BlogResponse,
    BlogUpdate,
)
from app.blog.services.blog import (
    create_blog,
    delete_blog,
    get_blog,
    get_blogs,
    update_blog,
)
from app.core.database import get_db


router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
)


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: BlogCreate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return create_blog(
        db=db,
        data=data,
        admin_id=admin.id,
    )


@router.get(
    "",
    response_model=list[BlogResponse],
)
def list_blogs(
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_blogs(db)


@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
)
def get(
    blog_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return get_blog(
        db=db,
        blog_id=blog_id,
    )


@router.patch(
    "/{blog_id}",
    response_model=BlogResponse,
)
def update(
    blog_id: UUID,
    data: BlogUpdate,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    return update_blog(
        db=db,
        blog_id=blog_id,
        data=data,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    blog_id: UUID,
    db: Session = Depends(get_db),
    admin: AdminProfile = Depends(get_current_admin),
):
    delete_blog(
        db=db,
        blog_id=blog_id,
    )