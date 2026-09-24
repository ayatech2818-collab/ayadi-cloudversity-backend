from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.config import settings
from app.auth.routes.auth import router as auth_router
from app.blog.routes.blog import router as blog_router
from app.blog.routes.author import router as author_router
from app.core.routes.upload import router as upload_router
from app.gallery.routes.gallery import router as gallery_router
from app.gallery.routes.gallery_item import router as gallery_item_router





app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    blog_router,
    prefix="/api/v1",
    tags=["Blogs"],
)
app.include_router(
    author_router,
    prefix="/api/v1",
)
app.include_router(
    upload_router,
    prefix="/api/v1",
)


app.include_router(
    gallery_router,
    prefix="/api/v1",
)

app.include_router(
    gallery_item_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {
        "message": "Ayadi Cloudversity API is running fine"
    }