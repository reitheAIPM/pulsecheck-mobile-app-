from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# SQLAlchemy Base for model definitions
Base = declarative_base()

class Database:
    """Database connection manager for Supabase"""
    
    def __init__(self):
        self.client: Client = None
        self._connected = False
    
    def connect(self):
        """Initialize Supabase client connection"""
        if self._connected:
            return
            
        try:
            self.client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key
            )
            self._connected = True
            logger.info("✅ Connected to Supabase database")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self._connected:
            self.connect()
        return self.client
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            if not self._connected:
                self.connect()
            # Simple query to check connection
            result = self.client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# SQLAlchemy setup for direct PostgreSQL access
def get_database_url() -> str:
    """Get PostgreSQL connection URL from Supabase URL"""
    try:
        # Convert Supabase URL to PostgreSQL URL
        supabase_url = settings.supabase_url
        if not supabase_url:
            logger.warning("SUPABASE_URL not set, using default database URL")
            return "sqlite:///./test.db"  # Fallback for development
            
        # Extract the project reference from supabase URL
        # Format: https://[project-ref].supabase.co
        project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')
        
        # Use environment variable for DB password if available, otherwise use service key
        db_password = os.environ.get('DB_PASSWORD', settings.supabase_service_key or 'password')
        
        # Construct PostgreSQL URL
        # Format: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
        database_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        logger.debug(f"Database URL constructed for project: {project_ref}")
        return database_url
    except Exception as e:
        logger.error(f"Failed to construct database URL: {e}")
        return "sqlite:///./fallback.db"  # Emergency fallback

# Global database instance (lazy initialization)
_db_instance = None

def get_database() -> Database:
    """Dependency to get database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

# SQLAlchemy session management
engine = None
SessionLocal = None

def get_db() -> Session:
    """Dependency to get SQLAlchemy database session"""
    global engine, SessionLocal
    
    if engine is None:
        try:
            database_url = get_database_url()
            logger.info(f"Initializing database engine...")
            engine = create_engine(database_url, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("✅ Database engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database engine: {e}")
            # Create a dummy engine to prevent NoneType errors
            engine = create_engine("sqlite:///./emergency.db")
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    if SessionLocal is None:
        logger.error("SessionLocal is None, creating emergency session")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 