"""
Check-ins Router - Minimal version for Railway deployment fix

Handles daily mood tracking, wellness check-ins, and user data retrieval.
Follows the API specification from ai/api-endpoints.md
"""

from fastapi import APIRouter

router = APIRouter(tags=["check-ins"])

@router.get("/health")
async def checkins_health():
    """Basic health check for checkins router"""
    return {"status": "ok", "message": "Checkins router is operational"}

# All other endpoints temporarily disabled for Railway deployment
# Will re-enable after authentication system is stabilized 
