#!/usr/bin/env python3
"""
Minimal PulseCheck API for debugging startup issues
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 Starting Minimal PulseCheck API")

app = FastAPI(
    title="PulseCheck API - Minimal",
    description="Minimal version for debugging",
    version="2.1.2-minimal",
)

# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PulseCheck API - Minimal Version", "version": "2.1.2-minimal", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pulsecheck-minimal"}

# Try to register just the adaptive AI router
try:
    print("🔄 Importing adaptive AI router...")
    from app.routers.adaptive_ai import router as adaptive_ai_router
    print("✅ Adaptive AI router imported successfully")
    
    app.include_router(adaptive_ai_router, prefix="/api/v1/adaptive-ai", tags=["adaptive-ai"])
    print("✅ Adaptive AI router registered")
    
except Exception as e:
    print(f"❌ Adaptive AI router failed: {e}")
    import traceback
    print(f"❌ Traceback: {traceback.format_exc()}")

# Try to register auth router
try:
    print("🔄 Importing auth router...")
    from app.routers.auth import router as auth_router
    print("✅ Auth router imported successfully")
    
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
    print("✅ Auth router registered")
    
except Exception as e:
    print(f"❌ Auth router failed: {e}")
    import traceback
    print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 