from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.auth.models.admin_profile import AdminProfile
from app.core.database import get_db
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.supabase import supabase


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        response = supabase.auth.get_claims(jwt=token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    if not response or not response.get("claims"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return response["claims"]

def get_current_admin(
    claims: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = claims.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    admin = db.scalar(
        select(AdminProfile).where(
            AdminProfile.id == user_id,
            AdminProfile.is_active.is_(True),
            AdminProfile.role == "admin",
        )
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return admin