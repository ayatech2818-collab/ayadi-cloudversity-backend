from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile


router = APIRouter()


@router.get("/me")
def get_current_admin_profile(
    admin: AdminProfile = Depends(get_current_admin),
):
    return {
        "id": str(admin.id),
        "full_name": admin.full_name,
        "role": admin.role,
        "is_active": admin.is_active,
    }