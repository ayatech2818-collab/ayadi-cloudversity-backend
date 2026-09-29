from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, UploadFile, Form, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.courses.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.courses.schemas.course_brand import (
    CourseBrandCreate,
    CourseBrandResponse,
    CourseBrandUpdate,
)
from app.courses.schemas.course_category import (
    CourseCategoryCreate,
    CourseCategoryResponse,
    CourseCategoryUpdate,
)
from app.courses.schemas.course_subcategory import (
    CourseSubcategoryCreate,
    CourseSubcategoryResponse,
    CourseSubcategoryUpdate,
)
from app.courses.services import course_service


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


# =========================================================
# Brands
# =========================================================

@router.post(
    "/brands",
    response_model=CourseBrandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_brand(
    name: str = Form(...),
    slug: str = Form(...),
    description: str | None = Form(None),
    is_active: bool = Form(True),
    display_order: int = Form(0),
    logo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    data = CourseBrandCreate(
        name=name,
        slug=slug,
        description=description,
        is_active=is_active,
        display_order=display_order,
    )

    return course_service.create_brand(
        db,
        data,
        logo,
    )


@router.get(
    "/brands",
    response_model=list[CourseBrandResponse],
)
def get_brands(
    db: Session = Depends(get_db),
):
    return course_service.get_brands(db)


@router.get(
    "/brands/{brand_id}",
    response_model=CourseBrandResponse,
)
def get_brand(
    brand_id: UUID,
    db: Session = Depends(get_db),
):
    return course_service.get_brand(db, brand_id)


@router.put(
    "/brands/{brand_id}",
    response_model=CourseBrandResponse,
)
def update_brand(
    brand_id: UUID,
    name: str | None = Form(None),
    slug: str | None = Form(None),
    description: str | None = Form(None),
    is_active: bool | None = Form(None),
    display_order: int | None = Form(None),
    logo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    update_data = {}

    if name is not None:
        update_data["name"] = name

    if slug is not None:
        update_data["slug"] = slug

    if description is not None:
        update_data["description"] = description

    if is_active is not None:
        update_data["is_active"] = is_active

    if display_order is not None:
        update_data["display_order"] = display_order

    data = CourseBrandUpdate(**update_data)

    return course_service.update_brand(
        db,
        brand_id,
        data,
        logo,
    )


@router.delete(
    "/brands/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_brand(
    brand_id: UUID,
    db: Session = Depends(get_db),
):
    course_service.delete_brand(db, brand_id)


# =========================================================
# Categories
# =========================================================

@router.post(
    "/categories",
    response_model=CourseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CourseCategoryCreate,
    db: Session = Depends(get_db),
):
    return course_service.create_category(db, data)


@router.get(
    "/categories",
    response_model=list[CourseCategoryResponse],
)
def get_categories(
    brand_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return course_service.get_categories(
        db,
        brand_id,
    )


@router.get(
    "/categories/{category_id}",
    response_model=CourseCategoryResponse,
)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    return course_service.get_category(
        db,
        category_id,
    )


@router.put(
    "/categories/{category_id}",
    response_model=CourseCategoryResponse,
)
def update_category(
    category_id: UUID,
    data: CourseCategoryUpdate,
    db: Session = Depends(get_db),
):
    return course_service.update_category(
        db,
        category_id,
        data,
    )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    course_service.delete_category(
        db,
        category_id,
    )


# =========================================================
# Subcategories
# =========================================================

@router.post(
    "/subcategories",
    response_model=CourseSubcategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_subcategory(
    data: CourseSubcategoryCreate,
    db: Session = Depends(get_db),
):
    return course_service.create_subcategory(
        db,
        data,
    )


@router.get(
    "/subcategories",
    response_model=list[CourseSubcategoryResponse],
)
def get_subcategories(
    category_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return course_service.get_subcategories(
        db,
        category_id,
    )


@router.get(
    "/subcategories/{subcategory_id}",
    response_model=CourseSubcategoryResponse,
)
def get_subcategory(
    subcategory_id: UUID,
    db: Session = Depends(get_db),
):
    return course_service.get_subcategory(
        db,
        subcategory_id,
    )


@router.put(
    "/subcategories/{subcategory_id}",
    response_model=CourseSubcategoryResponse,
)
def update_subcategory(
    subcategory_id: UUID,
    data: CourseSubcategoryUpdate,
    db: Session = Depends(get_db),
):
    return course_service.update_subcategory(
        db,
        subcategory_id,
        data,
    )


@router.delete(
    "/subcategories/{subcategory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subcategory(
    subcategory_id: UUID,
    db: Session = Depends(get_db),
):
    course_service.delete_subcategory(
        db,
        subcategory_id,
    )


# =========================================================
# Courses
# =========================================================

@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    brand_id: UUID = Form(...),
    category_id: UUID = Form(...),
    subcategory_id: UUID = Form(...),
    title: str = Form(...),
    slug: str = Form(...),
    course_code: str = Form(...),
    short_description: str | None = Form(None),
    description: str | None = Form(None),
    duration: str | None = Form(None),
    level: str | None = Form(None),
    is_published: bool = Form(False),
    display_order: int = Form(0),
    thumbnail: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    data = CourseCreate(
        brand_id=brand_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        title=title,
        slug=slug,
        course_code=course_code,
        short_description=short_description,
        description=description,
        duration=duration,
        level=level,
        is_published=is_published,
        display_order=display_order,
    )

    return course_service.create_course(
        db,
        data,
        thumbnail,
    )


@router.get(
    "",
    response_model=list[CourseResponse],
)
def get_courses(
    brand_id: UUID | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    subcategory_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return course_service.get_courses(
        db,
        brand_id,
        category_id,
        subcategory_id,
    )


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
)
def get_course(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    return course_service.get_course(
        db,
        course_id,
    )


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
)
def update_course(
    course_id: UUID,
    brand_id: UUID | None = Form(None),
    category_id: UUID | None = Form(None),
    subcategory_id: UUID | None = Form(None),
    title: str | None = Form(None),
    slug: str | None = Form(None),
    course_code: str | None = Form(None),
    short_description: str | None = Form(None),
    description: str | None = Form(None),
    duration: str | None = Form(None),
    level: str | None = Form(None),
    is_published: bool | None = Form(None),
    display_order: int | None = Form(None),
    thumbnail: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    update_data = {}

    if brand_id is not None:
        update_data["brand_id"] = brand_id

    if category_id is not None:
        update_data["category_id"] = category_id

    if subcategory_id is not None:
        update_data["subcategory_id"] = subcategory_id

    if title is not None:
        update_data["title"] = title

    if slug is not None:
        update_data["slug"] = slug

    if course_code is not None:
        update_data["course_code"] = course_code

    if short_description is not None:
        update_data["short_description"] = short_description

    if description is not None:
        update_data["description"] = description

    if duration is not None:
        update_data["duration"] = duration

    if level is not None:
        update_data["level"] = level

    if is_published is not None:
        update_data["is_published"] = is_published

    if display_order is not None:
        update_data["display_order"] = display_order

    data = CourseUpdate(**update_data)

    return course_service.update_course(
        db,
        course_id,
        data,
        thumbnail,
    )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    course_service.delete_course(
        db,
        course_id,
    )