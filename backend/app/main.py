
from fastapi import FastAPI

from app.api.employee_shift_assignment import (
    router as employee_shift_assignment_router,
)
from app.api.auth import router as auth_router

from app.api.organization_membership import (
    router as organization_membership_router,
)


app = FastAPI(
    title="SmartWash AI API",
    description="AI-powered car wash booking and management platform",
    version="1.0.0",
)

# Register Employee Scheduling API
app.include_router(employee_shift_assignment_router)

# Register Authentication API
app.include_router(auth_router)

# Register Organization Membership API
app.include_router(organization_membership_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to SmartWash AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartWash AI Backend",
    }

from app.api.organization_membership import (
    router as organization_membership_router,
)
