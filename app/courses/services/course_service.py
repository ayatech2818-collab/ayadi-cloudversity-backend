from uuid import UUID

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from app.core.storage import upload_image, delete_file

from app.courses.models.course import Course
from app.courses.models.course_brand import CourseBrand
from app.courses.models.course_category import CourseCategory
from app.courses.models.course_subcategory import CourseSubcategory
from app.courses.schemas.course import CourseCreate, CourseUpdate
from app.courses.schemas.course_brand import (
    CourseBrandCreate,
    CourseBrandUpdate,
)
from app.courses.schemas.course_category import (
    CourseCategoryCreate,
    CourseCategoryUpdate,
)
from app.courses.schemas.course_subcategory import (
    CourseSubcategoryCreate,
    CourseSubcategoryUpdate,
)


# =========================================================
# Course Brand
# =========================================================

def create_brand(
    db: Session,
    data: CourseBrandCreate,
    logo: UploadFile | None = None,
) -> CourseBrand:

    existing = db.scalar(
        select(CourseBrand).where(
            CourseBrand.slug == data.slug
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand slug already exists",
        )

    logo_url = None
    logo_key = None

    if logo:
        uploaded_logo = upload_image(
            logo,
            "course-brands",
        )

        logo_url = uploaded_logo["url"]
        logo_key = uploaded_logo["key"]

    brand = CourseBrand(
        **data.model_dump(),
        logo_url=logo_url,
        logo_key=logo_key,
    )

    try:
        db.add(brand)
        db.commit()
        db.refresh(brand)

    except Exception:
        db.rollback()

        # If database insertion fails after S3 upload,
        # remove the uploaded file.
        if logo_key:
            delete_file(logo_key)

        raise

    return brand


def get_brands(
    db: Session,
) -> list[CourseBrand]:

    return db.scalars(
        select(CourseBrand)
        .order_by(
            CourseBrand.display_order,
            CourseBrand.name,
        )
    ).all()


def get_brand(
    db: Session,
    brand_id: UUID,
) -> CourseBrand:

    brand = db.scalar(
        select(CourseBrand).where(
            CourseBrand.id == brand_id
        )
    )

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    return brand


def update_brand(
    db: Session,
    brand_id: UUID,
    data: CourseBrandUpdate,
    logo: UploadFile | None = None,
) -> CourseBrand:

    brand = get_brand(db, brand_id)

    update_data = data.model_dump(
        exclude_unset=True
    )

    # ---------------------------------------------
    # Check slug
    # ---------------------------------------------

    if "slug" in update_data:

        existing = db.scalar(
            select(CourseBrand).where(
                CourseBrand.slug == update_data["slug"],
                CourseBrand.id != brand_id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand slug already exists",
            )

    # ---------------------------------------------
    # Upload new logo
    # ---------------------------------------------

    old_logo_key = brand.logo_key
    new_logo_key = None

    if logo:

        uploaded_logo = upload_image(
            logo,
            "course-brands",
        )

        update_data["logo_url"] = uploaded_logo["url"]
        update_data["logo_key"] = uploaded_logo["key"]

        new_logo_key = uploaded_logo["key"]

    # ---------------------------------------------
    # Update database
    # ---------------------------------------------

    try:

        for key, value in update_data.items():
            setattr(brand, key, value)

        db.commit()
        db.refresh(brand)

    except Exception:

        db.rollback()

        # Remove newly uploaded logo if DB update fails
        if new_logo_key:
            delete_file(new_logo_key)

        raise

    # ---------------------------------------------
    # Delete old logo after successful DB update
    # ---------------------------------------------

    if logo and old_logo_key:
        delete_file(old_logo_key)

    return brand


def delete_brand(
    db: Session,
    brand_id: UUID,
) -> None:

    brand = get_brand(db, brand_id)

    logo_key = brand.logo_key

    try:
        db.delete(brand)
        db.commit()

    except Exception:
        db.rollback()
        raise

    # Delete S3 file only after successful DB deletion
    if logo_key:
        delete_file(logo_key)


# =========================================================
# Course Category
# =========================================================

def create_category(
    db: Session,
    data: CourseCategoryCreate,
) -> CourseCategory:

    brand = get_brand(db, data.brand_id)

    if not brand.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add category to an inactive brand",
        )

    existing = db.scalar(
        select(CourseCategory).where(
            CourseCategory.brand_id == data.brand_id,
            CourseCategory.slug == data.slug,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category slug already exists for this brand",
        )

    category = CourseCategory(**data.model_dump())

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_categories(
    db: Session,
    brand_id: UUID | None = None,
) -> list[CourseCategory]:

    query = select(CourseCategory)

    if brand_id:
        query = query.where(
            CourseCategory.brand_id == brand_id
        )

    query = query.order_by(
        CourseCategory.display_order,
        CourseCategory.name,
    )

    return db.scalars(query).all()


def get_category(
    db: Session,
    category_id: UUID,
) -> CourseCategory:

    category = db.scalar(
        select(CourseCategory).where(
            CourseCategory.id == category_id
        )
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


def update_category(
    db: Session,
    category_id: UUID,
    data: CourseCategoryUpdate,
) -> CourseCategory:

    category = get_category(db, category_id)

    update_data = data.model_dump(exclude_unset=True)

    if "brand_id" in update_data:

        get_brand(db, update_data["brand_id"])

    if "slug" in update_data:

        brand_id = update_data.get(
            "brand_id",
            category.brand_id,
        )

        existing = db.scalar(
            select(CourseCategory).where(
                CourseCategory.brand_id == brand_id,
                CourseCategory.slug == update_data["slug"],
                CourseCategory.id != category_id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category slug already exists for this brand",
            )

    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category_id: UUID,
) -> None:

    category = get_category(db, category_id)

    db.delete(category)
    db.commit()


# =========================================================
# Course Subcategory
# =========================================================

def create_subcategory(
    db: Session,
    data: CourseSubcategoryCreate,
) -> CourseSubcategory:

    category = get_category(db, data.category_id)

    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add subcategory to an inactive category",
        )

    existing = db.scalar(
        select(CourseSubcategory).where(
            CourseSubcategory.category_id == data.category_id,
            CourseSubcategory.slug == data.slug,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory slug already exists for this category",
        )

    subcategory = CourseSubcategory(
        **data.model_dump()
    )

    db.add(subcategory)
    db.commit()
    db.refresh(subcategory)

    return subcategory


def get_subcategories(
    db: Session,
    category_id: UUID | None = None,
) -> list[CourseSubcategory]:

    query = select(CourseSubcategory)

    if category_id:
        query = query.where(
            CourseSubcategory.category_id == category_id
        )

    query = query.order_by(
        CourseSubcategory.display_order,
        CourseSubcategory.name,
    )

    return db.scalars(query).all()


def get_subcategory(
    db: Session,
    subcategory_id: UUID,
) -> CourseSubcategory:

    subcategory = db.scalar(
        select(CourseSubcategory).where(
            CourseSubcategory.id == subcategory_id
        )
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategory not found",
        )

    return subcategory


def update_subcategory(
    db: Session,
    subcategory_id: UUID,
    data: CourseSubcategoryUpdate,
) -> CourseSubcategory:

    subcategory = get_subcategory(
        db,
        subcategory_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    if "category_id" in update_data:

        get_category(
            db,
            update_data["category_id"],
        )

    if "slug" in update_data:

        category_id = update_data.get(
            "category_id",
            subcategory.category_id,
        )

        existing = db.scalar(
            select(CourseSubcategory).where(
                CourseSubcategory.category_id == category_id,
                CourseSubcategory.slug == update_data["slug"],
                CourseSubcategory.id != subcategory_id,
            )
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subcategory slug already exists for this category",
            )

    for key, value in update_data.items():
        setattr(subcategory, key, value)

    db.commit()
    db.refresh(subcategory)

    return subcategory


def delete_subcategory(
    db: Session,
    subcategory_id: UUID,
) -> None:

    subcategory = get_subcategory(
        db,
        subcategory_id,
    )

    db.delete(subcategory)
    db.commit()


# =========================================================
# Course
# =========================================================

def validate_course_hierarchy(
    db: Session,
    brand_id: UUID,
    category_id: UUID | None,
    subcategory_id: UUID | None,
) -> None:

    # Check brand
    brand = get_brand(db, brand_id)

    if not brand.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand is inactive",
        )

    # Check whether this brand has any categories
    has_categories = db.scalar(
        select(
            exists().where(
                CourseCategory.brand_id == brand_id,
                CourseCategory.is_active.is_(True),
            )
        )
    )

    # ---------------------------------------------------------
    # Brand has NO categories → direct course
    # ---------------------------------------------------------
    if not has_categories:

        if category_id is not None or subcategory_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "This brand does not have categories. "
                    "Category and subcategory must be empty."
                ),
            )

        return

    # ---------------------------------------------------------
    # Brand HAS categories → category + subcategory required
    # ---------------------------------------------------------
    if category_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is required for this brand",
        )

    if subcategory_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory is required for this brand",
        )

    # Check category
    category = get_category(
        db,
        category_id,
    )

    if category.brand_id != brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category does not belong to the selected brand",
        )

    if not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is inactive",
        )

    # Check subcategory
    subcategory = get_subcategory(
        db,
        subcategory_id,
    )

    if subcategory.category_id != category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory does not belong to the selected category",
        )

    if not subcategory.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subcategory is inactive",
        )


def create_course(
    db: Session,
    data: CourseCreate,
    thumbnail: UploadFile | None = None,
) -> Course:

    validate_course_hierarchy(
        db,
        data.brand_id,
        data.category_id,
        data.subcategory_id,
    )

    # Check slug
    existing_slug = db.scalar(
        select(Course).where(
            Course.slug == data.slug
        )
    )

    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course slug already exists",
        )

    # Check course code
    existing_code = db.scalar(
        select(Course).where(
            Course.course_code == data.course_code
        )
    )

    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists",
        )

    thumbnail_url = None
    thumbnail_key = None

    # Upload thumbnail
    if thumbnail:
        uploaded_thumbnail = upload_image(
            thumbnail,
            "courses",
        )

        thumbnail_url = uploaded_thumbnail["url"]
        thumbnail_key = uploaded_thumbnail["key"]

    course = Course(
        **data.model_dump(),
        thumbnail_url=thumbnail_url,
        thumbnail_key=thumbnail_key,
    )

    try:
        db.add(course)
        db.commit()
        db.refresh(course)

    except Exception:
        db.rollback()

        # Remove uploaded thumbnail if DB operation fails
        if thumbnail_key:
            delete_file(thumbnail_key)

        raise

    return course


def get_courses(
    db: Session,
    brand_id: UUID | None = None,
    category_id: UUID | None = None,
    subcategory_id: UUID | None = None,
    search: str | None = None,
    is_published: bool | None = None,
) -> list[Course]:

    query = select(Course)

    if brand_id:
        query = query.where(
            Course.brand_id == brand_id
        )

    if category_id:
        query = query.where(
            Course.category_id == category_id
        )

    if subcategory_id:
        query = query.where(
            Course.subcategory_id == subcategory_id
        )

    # Case-insensitive match on the course title, done by the database.
    search_term = search.strip() if search else ""

    if search_term:
        query = query.where(
            Course.title.ilike(f"%{search_term}%")
        )

    if is_published is not None:
        query = query.where(
            Course.is_published.is_(is_published)
        )

    query = query.order_by(
        Course.display_order,
        Course.title,
    )

    return db.scalars(query).all()


def get_course(
    db: Session,
    course_id: UUID,
) -> Course:

    course = db.scalar(
        select(Course).where(
            Course.id == course_id
        )
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course


def update_course(
    db: Session,
    course_id: UUID,
    data: CourseUpdate,
    thumbnail: UploadFile | None = None,
) -> Course:

    course = get_course(
        db,
        course_id,
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    brand_id = update_data.get(
        "brand_id",
        course.brand_id,
    )

    category_id = update_data.get(
        "category_id",
        course.category_id,
    )

    subcategory_id = update_data.get(
        "subcategory_id",
        course.subcategory_id,
    )

    # ---------------------------------------------------------
    # If brand is changed, determine whether the new brand
    # uses categories.
    # ---------------------------------------------------------

    has_categories = db.scalar(
        select(
            exists().where(
                CourseCategory.brand_id == brand_id,
                CourseCategory.is_active.is_(True),
            )
        )
    )

    # Direct-course brand
    if not has_categories:
        category_id = None
        subcategory_id = None

        update_data["category_id"] = None
        update_data["subcategory_id"] = None

    # Validate hierarchy for the selected brand
    validate_course_hierarchy(
        db,
        brand_id,
        category_id,
        subcategory_id,
    )

    # ---------------------------------------------------------
    # Check slug
    # ---------------------------------------------------------

    if "slug" in update_data:

        existing_slug = db.scalar(
            select(Course).where(
                Course.slug == update_data["slug"],
                Course.id != course_id,
            )
        )

        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course slug already exists",
            )

    # ---------------------------------------------------------
    # Check course code
    # ---------------------------------------------------------

    if "course_code" in update_data:

        existing_code = db.scalar(
            select(Course).where(
                Course.course_code == update_data["course_code"],
                Course.id != course_id,
            )
        )

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists",
            )

    # ---------------------------------------------------------
    # Thumbnail
    # ---------------------------------------------------------

    old_thumbnail_key = course.thumbnail_key
    new_thumbnail_key = None

    if thumbnail:

        uploaded_thumbnail = upload_image(
            thumbnail,
            "courses",
        )

        new_thumbnail_key = uploaded_thumbnail["key"]

        update_data["thumbnail_url"] = uploaded_thumbnail["url"]
        update_data["thumbnail_key"] = uploaded_thumbnail["key"]

    # ---------------------------------------------------------
    # Update database
    # ---------------------------------------------------------

    try:

        for key, value in update_data.items():
            setattr(course, key, value)

        db.commit()
        db.refresh(course)

    except Exception:

        db.rollback()

        # Remove newly uploaded thumbnail
        if new_thumbnail_key:
            delete_file(new_thumbnail_key)

        raise

    # ---------------------------------------------------------
    # Delete old thumbnail
    # ---------------------------------------------------------

    if thumbnail and old_thumbnail_key:
        delete_file(old_thumbnail_key)

    return course


def delete_course(
    db: Session,
    course_id: UUID,
) -> None:

    course = get_course(
        db,
        course_id,
    )

    thumbnail_key = course.thumbnail_key

    db.delete(course)
    db.commit()

    # Delete thumbnail from S3
    if thumbnail_key:
        delete_file(thumbnail_key)