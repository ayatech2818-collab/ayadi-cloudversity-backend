from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.config import settings
from app.auth.routes.auth import router as auth_router
from app.blog.routes.blog import router as blog_router
from app.blog.routes.author import router as author_router
from app.core.routes.upload import router as upload_router
from app.gallery.routes.gallery import router as gallery_router
from app.gallery.routes.gallery_item import router as gallery_item_router
from app.courses.routes.course_routes import router as course_router
from app.enquiries.routes.enquiry import router as enquiry_router
from app.dashboard.routes import router as dashboard_router

from fastapi.openapi.utils import get_openapi





app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    for component in schema.get("components", {}).get("schemas", {}).values():
        properties = component.get("properties", {})

        for prop in properties.values():

            # Single file
            if (
                prop.get("type") == "string"
                and prop.get("contentMediaType") == "application/octet-stream"
            ):
                prop.pop("contentMediaType", None)
                prop["format"] = "binary"

            # Multiple files
            items = prop.get("items")

            if (
                prop.get("type") == "array"
                and isinstance(items, dict)
                and items.get("contentMediaType") == "application/octet-stream"
            ):
                items.pop("contentMediaType", None)
                items["format"] = "binary"

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


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

app.include_router(
    course_router,
    prefix="/api/v1",
)
app.include_router(
    enquiry_router,
    prefix="/api/v1",
)
app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {
        "message": "Ayadi Cloudversity API is running fine"
    }