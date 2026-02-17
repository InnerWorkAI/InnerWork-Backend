# Main
from fastapi import FastAPI
from app.core.openapi_config import custom_openapi
from app.controllers import test


# Api configuration
app = FastAPI(
    title="InnerWork API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.openapi = lambda: custom_openapi(app)

# Include routers
app.include_router(test.router)