"""
User Service

Business logic for user management including CRUD operations,
profile updates, and user preferences.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
import uuid

from ..models.user import UserCreate, UserUpdate, UserTable
from ..core.database import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """Service class for user-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    async def get_user_by_id(db: Session, user_id: str) -> Optional[UserTable]:
        """Get user by ID"""
        try:
            # Convert string to UUID if needed
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
                
            return db.query(UserTable).filter(UserTable.id == user_id).first()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[UserTable]:
        """Get user by email address"""
        return db.query(UserTable).filter(UserTable.email == email).first()
    
    @staticmethod
    async def create_user(db: Session, user_data: UserCreate) -> UserTable:
        """Create a new user account"""
        # Hash the password
        hashed_password = UserService.hash_password(user_data.password)
        
        # Create user instance
        db_user = UserTable(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            timezone=user_data.timezone
        )
        
        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def update_user(
        db: Session, 
        user_id: str, 
        user_update: UserUpdate
    ) -> Optional[UserTable]:
        """Update user profile and preferences"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields that were provided
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_user(db: Session, user_id: str) -> bool:
        """Delete user account and all associated data"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # Delete user (cascade will handle related data)
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    async def get_user_stats(db: Session, user_id: str) -> dict:
        """Get user statistics for dashboard"""
        # Get basic user info
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return {}
        
        # Get check-in statistics
        stats_query = text("""
            SELECT 
                COUNT(*) as total_checkins,
                MAX(created_at) as last_checkin,
                AVG(mood_score) as avg_mood,
                AVG(energy_level) as avg_energy,
                AVG(stress_level) as avg_stress
            FROM checkins 
            WHERE user_id = :user_id
        """)
        
        result = db.execute(stats_query, {"user_id": user_id}).fetchone()
        
        return {
            "total_checkins": result[0] if result else 0,
            "last_checkin": result[1] if result else None,
            "avg_mood": round(result[2], 1) if result and result[2] else None,
            "avg_energy": round(result[3], 1) if result and result[3] else None,
            "avg_stress": round(result[4], 1) if result and result[4] else None,
            "member_since": user.created_at
        } 