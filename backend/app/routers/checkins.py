"""
Check-ins Router

Handles daily mood tracking, wellness check-ins, and user data retrieval.
Follows the API specification from ai/api-endpoints.md
"""

from datetime import datetime, timedelta
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.checkin import CheckInCreate, CheckInUpdate, CheckInResponse
from ..models.user import UserResponse
from ..routers.auth import get_current_user
from ..services.checkin_service import CheckInService

router = APIRouter(prefix="/checkins", tags=["check-ins"])

@router.post("/", response_model=CheckInResponse)
async def create_checkin(
    checkin_data: CheckInCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Submit daily check-in data
    
    Creates a new wellness check-in with mood, energy, stress levels,
    and optional journal entry and lifestyle factors.
    """
    # Set timestamp to now if not provided
    if checkin_data.timestamp is None:
        checkin_data.timestamp = datetime.now(timezone.utc)
    
    # Create check-in
    checkin = await CheckInService.create_checkin(
        db, 
        user_id=str(current_user.id), 
        checkin_data=checkin_data
    )
    
    return checkin

@router.get("/", response_model=List[CheckInResponse])
async def get_checkins(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    limit: int = Query(default=30, le=100, description="Number of check-ins to return"),
    offset: int = Query(default=0, ge=0, description="Number of check-ins to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter check-ins from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter check-ins until this date")
):
    """
    Retrieve user's check-in history
    
    Returns paginated list of user's check-ins with optional date filtering.
    """
    checkins = await CheckInService.get_user_checkins(
        db,
        user_id=str(current_user.id),
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date
    )
    
    return checkins

@router.get("/{checkin_id}", response_model=CheckInResponse)
async def get_checkin(
    checkin_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Get specific check-in details
    
    Returns detailed information about a specific check-in.
    Only the owner can access their check-ins.
    """
    checkin = await CheckInService.get_checkin_by_id(db, checkin_id)
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    # Verify ownership
    if str(checkin.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this check-in"
        )
    
    return checkin

@router.put("/{checkin_id}", response_model=CheckInResponse)
async def update_checkin(
    checkin_id: str,
    checkin_update: CheckInUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Update an existing check-in
    
    Allows users to modify their check-in data within a reasonable time window.
    """
    checkin = await CheckInService.get_checkin_by_id(db, checkin_id)
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    # Verify ownership
    if str(checkin.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this check-in"
        )
    
    # Check if check-in is too old to modify (24 hours)
    if datetime.now(timezone.utc) - checkin.created_at > timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in is too old to modify (24 hour limit)"
        )
    
    updated_checkin = await CheckInService.update_checkin(
        db, 
        checkin_id=checkin_id, 
        checkin_update=checkin_update
    )
    
    return updated_checkin

@router.delete("/{checkin_id}")
async def delete_checkin(
    checkin_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Delete a check-in
    
    Allows users to delete their check-ins within a reasonable time window.
    """
    checkin = await CheckInService.get_checkin_by_id(db, checkin_id)
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    # Verify ownership
    if str(checkin.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this check-in"
        )
    
    # Check if check-in is too old to delete (24 hours)
    if datetime.now(timezone.utc) - checkin.created_at > timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in is too old to delete (24 hour limit)"
        )
    
    success = await CheckInService.delete_checkin(db, checkin_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete check-in"
        )
    
    return {"message": "Check-in deleted successfully"}

@router.get("/stats/summary")
async def get_checkin_stats(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Session = Depends(get_db),
    days: int = Query(default=30, le=365, description="Number of days to include in stats")
):
    """
    Get check-in statistics summary
    
    Returns aggregated statistics for the user's check-ins over the specified period.
    """
    stats = await CheckInService.get_user_stats(
        db, 
        user_id=str(current_user.id), 
        days=days
    )
    
    return stats 
