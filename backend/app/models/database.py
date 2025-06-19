"""
PulseCheck Database Models

Consolidated SQLAlchemy table definitions for database schema management.
This file imports all table models and provides a single Base for migrations.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Import all table models
from .user import UserTable
from .checkin import CheckInTable  
from .ai_analysis import AIAnalysisTable

# Single declarative base for all models
Base = declarative_base()

# Re-create tables with unified base
class User(UserTable, Base):
    __tablename__ = "users"

class CheckIn(CheckInTable, Base):
    __tablename__ = "checkins"

class AIAnalysis(AIAnalysisTable, Base):
    __tablename__ = "ai_analyses"

# Export all models
__all__ = [
    "Base",
    "User", 
    "CheckIn",
    "AIAnalysis"
] 