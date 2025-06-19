from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and routers
from app.core.config import settings
from app.routers import auth, checkins

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 PulseCheck API starting up...")
    print(f"🌍 Environment: {settings.environment}")
    print(f"🔗 CORS Origins: {settings.allowed_origins_list}")
    yield
    # Shutdown
    print("👋 PulseCheck API shutting down...")

app = FastAPI(
    title="PulseCheck API",
    description="AI-powered burnout prevention for tech workers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PulseCheck API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "PulseCheck API",
        "version": "1.0.0",
        "environment": settings.environment
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(checkins.router, prefix="/api/v1", tags=["check-ins"])
# app.include_router(ai_insights.router, prefix="/api/v1/ai", tags=["ai-insights"])
# app.include_router(user.router, prefix="/api/v1/user", tags=["user"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port) 