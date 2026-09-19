from fastapi import FastAPI


from app.core.config import settings
from app.auth.routes.auth import router as auth_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@app.get("/")
def root():
    return {
        "message": "Ayadi Cloudversity API is running fine"
    }