from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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

# CORS configuration for React Native and Railway health checks
if config_loaded:
    cors_origins = settings.allowed_origins_list
else:
    cors_origins = ["*"]  # Allow all origins if config failed

# Add Railway health check domain to allowed origins
railway_health_check = "healthcheck.railway.app"
if railway_health_check not in cors_origins and "*" not in cors_origins:
    cors_origins.append(railway_health_check)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Global OPTIONS handler for Railway health checks
@app.options("/{full_path:path}")
async def global_options_handler(full_path: str):
    """Handle all OPTIONS requests for Railway health check compatibility"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        }
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PulseCheck API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check with OpenAI status - v2.1 with CORS fixes - FORCE DEPLOY"""
    # Check OpenAI configuration
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_configured = bool(openai_api_key and openai_api_key.startswith('sk-'))
    
    return {
        "status": "healthy",
        "service": "PulseCheck API",
        "version": "2.1.0-cors-fix",
        "timestamp": "2025-01-20T22:30:00Z",
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "config_loaded": True,
        "openai_configured": openai_configured,
        "openai_status": "configured" if openai_configured else "disabled (billing not set up)"
    }

@app.options("/health")
async def health_check_options():
    """Handle OPTIONS requests for health check (Railway health check compatibility)"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        }
    )

@app.get("/docs")
async def api_documentation():
    """Simple API documentation endpoint"""
    return {
        "message": "PulseCheck API Documentation",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "root": "/ - API status endpoint",
            "journal": "/api/v1/journal/* - Journal entry management",
            "auth": "/api/v1/auth/* - Authentication endpoints",
            "checkins": "/api/v1/checkins/* - Check-in endpoints",
            "admin": "/api/v1/admin/* - Admin analytics endpoints"
        },
        "swagger_ui": "/docs" if config_loaded else "Not available (config not loaded)",
        "openapi_spec": "/openapi.json" if config_loaded else "Not available (config not loaded)"
    }

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