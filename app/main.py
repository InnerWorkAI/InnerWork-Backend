# Main
import logging
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.controllers import auth_controller, test, user_controller, company_controller, weekly_burnout_form_controller, employee_controller
from app.models.employee_model import EmployeeModel

# Configurar logger de Uvicorn
logger = logging.getLogger("uvicorn")

# Api configuration
app = FastAPI(
    title="InnerWork API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Create database tables if they don't exist 
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(test.router)
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(company_controller.router)
app.include_router(employee_controller.router)
app.include_router(weekly_burnout_form_controller.router)