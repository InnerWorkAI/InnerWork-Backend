# Main
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.core.openapi_config import custom_openapi
from app.controllers import test, user_controller, company_controller


# Api configuration
app = FastAPI(
    title="InnerWork API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.openapi = lambda: custom_openapi(app)

# Crear tablas automáticamente (solo dev)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(test.router)
app.include_router(user_controller.router)
app.include_router(company_controller.router)
