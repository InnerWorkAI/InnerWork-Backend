# Main
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.base import Base
from app.db.session import engine
from app.controllers import (
    auth_controller,
    test,
    user_controller,
    company_controller,
    weekly_burnout_form_controller,
    employee_controller,
    image_predictor_controller
)

logger = logging.getLogger("uvicorn")

app = FastAPI(
    title="InnerWork API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"], # Permite a tu Ionic/Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables if they don't exist 
Base.metadata.create_all(bind=engine)

# Create uploads directory if it doesn't exist
os.makedirs("uploads/profile_images", exist_ok=True)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(test.router)
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(company_controller.router)
app.include_router(employee_controller.router)
app.include_router(weekly_burnout_form_controller.router)
app.include_router(image_predictor_controller.router)