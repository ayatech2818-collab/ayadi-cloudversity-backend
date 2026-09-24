import uuid

import boto3

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_GALLERY_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

def upload_gallery_file(
    file: UploadFile,
    gallery_id: str,
) -> dict[str, str | int | None]:
    allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_GALLERY_VIDEO_TYPES

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WebP, MP4, WebM, and MOV files are allowed.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    extension = file.filename.rsplit(".", 1)[-1].lower()

    file_id = uuid.uuid4()

    storage_key = f"galleries/{gallery_id}/{file_id}.{extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET,
            storage_key,
            ExtraArgs={
                "ContentType": file.content_type,
            },
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload gallery file.",
        )

    file_url = (
        f"https://{settings.AWS_S3_BUCKET}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{storage_key}"
    )

    if file.content_type in ALLOWED_IMAGE_TYPES:
        media_type = "image"
    else:
        media_type = "video"

    return {
        "file_name": file.filename,
        "url": file_url,
        "key": storage_key,
        "media_type": media_type,
        "mime_type": file.content_type,
        "file_size": None,
    }

def upload_image(
    file: UploadFile,
    folder: str,
) -> dict[str, str]:

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed.",
        )

    extension = file.filename.rsplit(".", 1)[-1].lower()

    file_id = uuid.uuid4()

    storage_key = f"{folder}/{file_id}.{extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET,
            storage_key,
            ExtraArgs={
                "ContentType": file.content_type,
            },
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image.",
        )

    file_url = (
        f"https://{settings.AWS_S3_BUCKET}.s3."
        f"{settings.AWS_REGION}.amazonaws.com/{storage_key}"
    )

    return {
        "url": file_url,
        "key": storage_key,
    }

def delete_file(storage_key: str) -> None:
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=storage_key,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file from storage.",
        )