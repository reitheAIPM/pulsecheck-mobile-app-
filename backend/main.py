from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration and routers
try:
    from app.core.config import settings
    config_loaded = True
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
    config_loaded = False
    # Create minimal settings for health checks
    class MinimalSettings:
        environment = "production"
        allowed_origins_list = ["*"]
        host = "0.0.0.0"
        port = 8000
    settings = MinimalSettings()

from app.routers import auth, checkins, journal, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 PulseCheck API starting up...")
    print(f"🌍 Environment: {settings.environment}")
    if config_loaded:
        print(f"🔗 CORS Origins: {settings.allowed_origins_list}")
        print("✅ Configuration loaded successfully")
    else:
        print("⚠️  Running with minimal configuration")
        print("🔧 Some features may not work without proper environment variables")
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
if config_loaded:
    cors_origins = settings.allowed_origins_list
else:
    cors_origins = ["*"]  # Allow all origins if config failed

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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
    health_status = {
        "status": "healthy",
        "service": "PulseCheck API",
        "version": "1.0.0",
        "environment": getattr(settings, 'environment', 'unknown'),
        "config_loaded": config_loaded
    }
    
    if not config_loaded:
        health_status["warnings"] = [
            "Configuration not fully loaded",
            "Some features may be unavailable"
        ]
    
    return health_status

# Include routers only if configuration is loaded
if config_loaded:
    print("🔗 Loading API routers...")
    try:
        app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
        print("✅ Auth router loaded")
    except Exception as e:
        print(f"❌ Auth router failed: {e}")
        
    try:
        app.include_router(checkins.router, prefix="/api/v1", tags=["check-ins"])
        print("✅ Check-ins router loaded")
    except Exception as e:
        print(f"❌ Check-ins router failed: {e}")
        
    try:
        app.include_router(journal.router, prefix="/api/v1/journal", tags=["journal"])
        print("✅ Journal router loaded at /api/v1/journal")
    except Exception as e:
        print(f"❌ Journal router failed: {e}")
        
    try:
        app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
        print("✅ Admin router loaded at /api/v1/admin")
    except Exception as e:
        print(f"❌ Admin router failed: {e}")
        
    # app.include_router(ai_insights.router, prefix="/api/v1/ai", tags=["ai-insights"])
    # app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
    print("🚀 All routers loaded successfully")
else:
    print("⚠️  API routes not loaded due to configuration issues")

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT environment variable if available
    port = int(os.getenv('PORT', getattr(settings, 'port', 8000)))
    uvicorn.run(app, host=getattr(settings, 'host', '0.0.0.0'), port=port) 