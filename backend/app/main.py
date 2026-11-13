
from fastapi import FastAPI

app = FastAPI(
    title="SmartWash AI API",
    description="AI-powered car wash booking and management platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to SmartWash AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartWash AI Backend"
    }
