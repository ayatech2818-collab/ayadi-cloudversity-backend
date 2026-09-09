from fastapi import FastAPI

from app.core.config import settings
from app.core.database import test_db_connection


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.on_event("startup")
def startup():
    test_db_connection()


@app.get("/")
def root():
    return {
        "message": "Ayadi Cloudversity API is running"
    }