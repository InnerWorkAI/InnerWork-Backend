import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import gc

from app.db.base import Base
from app.db.session import engine
from app.controllers import (
    auth_controller,
    test,
    user_controller,
    company_controller,
    weekly_burnout_form_controller,
    employee_controller,
    image_predictor_controller,
    audio_predictor_controller
)
from app.tasks.reminder_tasks import start_scheduler
from app.seeders.development_seed import run_development_seed
from app.core.config import settings

# Logging configuration
log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log_file = "logs/innerwork.log"
os.makedirs("logs", exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger("InnerWorkAPI")
logger.info("Starting InnerWork API...")

# FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application lifespan...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    # Run development seed if in development environment
    if settings.ENV == "development":
        logger.info("Running development seed...")
        run_development_seed()

    # Start scheduler
    logger.info("Starting background scheduler...")
    start_scheduler()
    
    yield
    logger.info("Application shutting down...")

# FastAPI app instance
app = FastAPI(
    title="InnerWork API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.innerwork-ai.es",
        "http://localhost:4200",
        "https://uptimerobot.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(audio_predictor_controller.router)

logger.info("All routers loaded successfully.")