"""
Check-in Service

Business logic for daily check-ins, mood tracking, and wellness data management.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
import uuid

from ..models.checkin import CheckInCreate, CheckInUpdate, CheckInTable

class CheckInService:
    """Service class for check-in related operations"""
    
    @staticmethod
    async def create_checkin(
        db: Session, 
        user_id: str, 
        checkin_data: CheckInCreate
    ) -> CheckInTable:
        """Create a new check-in"""
        # Convert user_id to UUID if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        # Set timestamp to now if not provided
        timestamp = checkin_data.timestamp or datetime.utcnow()
        
        # Create check-in instance
        db_checkin = CheckInTable(
            user_id=user_id,
            mood_score=checkin_data.mood_score,
            energy_level=checkin_data.energy_level,
            stress_level=checkin_data.stress_level,
            journal_entry=checkin_data.journal_entry,
            sleep_hours=checkin_data.sleep_hours,
            work_hours=checkin_data.work_hours,
            exercise_minutes=checkin_data.exercise_minutes,
            tags=checkin_data.tags,
            timestamp=timestamp
        )
        
        # Save to database
        db.add(db_checkin)
        db.commit()
        db.refresh(db_checkin)
        
        return db_checkin
    
    @staticmethod
    async def get_checkin_by_id(db: Session, checkin_id: str) -> Optional[CheckInTable]:
        """Get check-in by ID"""
        try:
            # Convert string to UUID if needed
            if isinstance(checkin_id, str):
                checkin_id = uuid.UUID(checkin_id)
                
            return db.query(CheckInTable).filter(CheckInTable.id == checkin_id).first()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    async def get_user_checkins(
        db: Session,
        user_id: str,
        limit: int = 30,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CheckInTable]:
        """Get user's check-ins with optional filtering"""
        try:
            # Convert user_id to UUID if needed
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except (ValueError, TypeError):
            return []
        
        query = db.query(CheckInTable).filter(CheckInTable.user_id == user_id)
        
        # Apply date filters
        if start_date:
            query = query.filter(CheckInTable.timestamp >= start_date)
        if end_date:
            query = query.filter(CheckInTable.timestamp <= end_date)
        
        # Order by timestamp descending (most recent first)
        query = query.order_by(desc(CheckInTable.timestamp))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()
    
    @staticmethod
    async def update_checkin(
        db: Session,
        checkin_id: str,
        checkin_update: CheckInUpdate
    ) -> Optional[CheckInTable]:
        """Update an existing check-in"""
        checkin = await CheckInService.get_checkin_by_id(db, checkin_id)
        if not checkin:
            return None
        
        # Update fields that were provided
        update_data = checkin_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(checkin, field, value)
        
        db.commit()
        db.refresh(checkin)
        
        return checkin
    
    @staticmethod
    async def delete_checkin(db: Session, checkin_id: str) -> bool:
        """Delete a check-in"""
        checkin = await CheckInService.get_checkin_by_id(db, checkin_id)
        if not checkin:
            return False
        
        db.delete(checkin)
        db.commit()
        
        return True
    
    @staticmethod
    async def get_user_stats(db: Session, user_id: str, days: int = 30) -> dict:
        """Get user's check-in statistics for the specified period"""
        try:
            # Convert user_id to UUID if needed
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except (ValueError, TypeError):
            return {}
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get statistics using raw SQL for better performance
        stats_query = text("""
            SELECT 
                COUNT(*) as total_checkins,
                AVG(mood_score) as avg_mood,
                AVG(energy_level) as avg_energy,
                AVG(stress_level) as avg_stress,
                AVG(sleep_hours) as avg_sleep,
                AVG(work_hours) as avg_work,
                AVG(exercise_minutes) as avg_exercise,
                MAX(timestamp) as last_checkin,
                MIN(timestamp) as first_checkin,
                COUNT(CASE WHEN journal_entry IS NOT NULL AND journal_entry != '' THEN 1 END) as journal_entries
            FROM checkins 
            WHERE user_id = :user_id 
            AND timestamp >= :start_date 
            AND timestamp <= :end_date
        """)
        
        result = db.execute(stats_query, {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }).fetchone()
        
        if not result or result[0] == 0:
            return {
                "period_days": days,
                "total_checkins": 0,
                "message": "No check-ins found for this period"
            }
        
        # Get mood trend (last 7 days vs previous 7 days)
        trend_query = text("""
            WITH recent AS (
                SELECT AVG(mood_score) as avg_mood
                FROM checkins 
                WHERE user_id = :user_id 
                AND timestamp >= :recent_start
                AND timestamp <= :end_date
            ),
            previous AS (
                SELECT AVG(mood_score) as avg_mood
                FROM checkins 
                WHERE user_id = :user_id 
                AND timestamp >= :prev_start
                AND timestamp < :recent_start
            )
            SELECT recent.avg_mood, previous.avg_mood
            FROM recent, previous
        """)
        
        recent_start = end_date - timedelta(days=7)
        prev_start = end_date - timedelta(days=14)
        
        trend_result = db.execute(trend_query, {
            "user_id": user_id,
            "end_date": end_date,
            "recent_start": recent_start,
            "prev_start": prev_start
        }).fetchone()
        
        # Calculate trend
        mood_trend = None
        if trend_result and trend_result[0] is not None and trend_result[1] is not None:
            recent_mood = float(trend_result[0])
            previous_mood = float(trend_result[1])
            mood_change = recent_mood - previous_mood
            
            if abs(mood_change) < 0.5:
                mood_trend = "stable"
            elif mood_change > 0:
                mood_trend = "improving"
            else:
                mood_trend = "declining"
        
        return {
            "period_days": days,
            "total_checkins": result[0],
            "avg_mood": round(float(result[1]), 1) if result[1] else None,
            "avg_energy": round(float(result[2]), 1) if result[2] else None,
            "avg_stress": round(float(result[3]), 1) if result[3] else None,
            "avg_sleep": round(float(result[4]), 1) if result[4] else None,
            "avg_work_hours": round(float(result[5]), 1) if result[5] else None,
            "avg_exercise_minutes": round(float(result[6]), 1) if result[6] else None,
            "last_checkin": result[7],
            "first_checkin": result[8],
            "journal_entries": result[9],
            "journal_percentage": round((result[9] / result[0]) * 100, 1) if result[0] > 0 else 0,
            "mood_trend": mood_trend,
            "checkin_frequency": round(result[0] / days, 2) if days > 0 else 0
        }
    
    @staticmethod
    async def get_recent_checkins_for_ai(
        db: Session, 
        user_id: str, 
        days: int = 7
    ) -> List[CheckInTable]:
        """Get recent check-ins for AI analysis"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return await CheckInService.get_user_checkins(
            db,
            user_id=user_id,
            limit=100,  # Get more data for AI analysis
            start_date=start_date,
            end_date=end_date
        ) 