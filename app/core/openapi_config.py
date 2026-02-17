from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="InnerWork API",
        version="1.0.0",
        description="API for InnerWork application",
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # Agregate security scheme for JWT authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Aplly security globally to all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
