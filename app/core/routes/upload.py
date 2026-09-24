from fastapi import APIRouter, Depends, File, UploadFile

from app.auth.dependencies import get_current_admin
from app.auth.models.admin_profile import AdminProfile
from app.core.schemas.upload import UploadResponse
from app.core.storage import upload_image


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


@router.post(
    "/image",
    response_model=UploadResponse,
)
def upload_image_file(
    file: UploadFile = File(...),
    admin: AdminProfile = Depends(get_current_admin),
):
    return upload_image(
        file=file,
        folder="images",
    )