from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
import logging
import os
import time
from typing import Optional
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

# SQLAlchemy Base for model definitions
Base = declarative_base()

class Database:
    """Optimized database connection manager for Supabase with connection pooling"""
    
    def __init__(self):
        self.client: Client = None
        self._connected = False
        self._connection_pool: dict = {}
        self._last_health_check = 0
        self._health_check_interval = 30  # Check every 30 seconds
    
    def connect(self):
        """Initialize Supabase client connection with optimizations"""
        if self._connected and self.client:
            return
            
        try:
            # Create optimized Supabase client
            self.client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY,
                options={
                    "connection_timeout": 10,  # 10 second timeout
                    "request_timeout": 30,     # 30 second request timeout
                    "retry_attempts": 3,       # Retry failed requests 3 times
                    "retry_delay": 1,          # 1 second delay between retries
                }
            )
            self._connected = True
            logger.info("✅ Connected to Supabase database with optimized settings")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance with health checking"""
        current_time = time.time()
        
        # Perform periodic health checks
        if current_time - self._last_health_check > self._health_check_interval:
            self._last_health_check = current_time
            if not self._is_connection_healthy():
                logger.warning("Database connection unhealthy, reconnecting...")
                self._connected = False
                self.connect()
        
        if not self._connected:
            self.connect()
        return self.client
    
    def _is_connection_healthy(self) -> bool:
        """Quick health check for database connection"""
        try:
            if not self.client:
                return False
            # Quick ping with timeout
            result = self.client.table('profiles').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    async def health_check(self) -> dict:
        """Enhanced health check with performance metrics"""
        start_time = time.time()
        try:
            if not self._connected:
                self.connect()
            
            # Test basic connectivity
            result = self.client.table('profiles').select('id').limit(1).execute()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connection_pool": len(self._connection_pool),
                "last_health_check": self._last_health_check
            }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(response_time, 2)
            }

@lru_cache(maxsize=1)
def get_database_url() -> str:
    """Get PostgreSQL connection URL from Supabase URL with caching"""
    try:
        # Convert Supabase URL to PostgreSQL URL
        supabase_url = settings.SUPABASE_URL
        if not supabase_url:
            logger.error("SUPABASE_URL not set - CRITICAL: No database configured!")
            raise ValueError("SUPABASE_URL environment variable is required")
            
        # Extract the project reference from supabase URL
        # Format: https://[project-ref].supabase.co
        project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')
        
        # Use environment variable for DB password if available, otherwise use service key
        db_password = os.environ.get('DB_PASSWORD', settings.SUPABASE_SERVICE_ROLE_KEY or 'password')
        
        # Construct PostgreSQL URL with connection pooling parameters
        database_url = (
            f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
            f"?sslmode=require&pool_size=10&max_overflow=20&pool_timeout=30&pool_recycle=3600"
        )
        logger.debug(f"Database URL constructed for project: {project_ref}")
        return database_url
    except Exception as e:
        logger.error(f"Failed to construct database URL: {e}")
        raise ValueError(f"Database configuration failed: {e}")

# Global database instance (singleton pattern)
_db_instance: Optional[Database] = None
_db_lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None

def get_database() -> Database:
    """Dependency to get database instance with thread safety"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.connect()  # Eager connection for better performance
    return _db_instance

# Export a global supabase client for direct use
supabase: Optional[Client] = None

def init_supabase() -> Client:
    """Initialize and return the global supabase client"""
    global supabase
    if supabase is None:
        try:
            db = get_database()
            supabase = db.get_client()
            logger.info("✅ Global Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize global supabase client: {e}")
            raise
    return supabase

# Initialize supabase on import with error handling
try:
    supabase = init_supabase()
except Exception as e:
    logger.warning(f"Failed to initialize supabase on import: {e}")
    supabase = None

# Optimized SQLAlchemy session management
engine = None
SessionLocal = None

def create_optimized_engine():
    """Create SQLAlchemy engine with performance optimizations"""
    global engine, SessionLocal
    
    if engine is not None:
        return engine
        
    try:
        database_url = get_database_url()
        logger.info("Initializing optimized database engine...")
        
        # Create engine with performance optimizations
        engine = create_engine(
            database_url,
            echo=False,  # Disable query logging for performance
            pool_size=10,           # Connection pool size
            max_overflow=20,        # Additional connections beyond pool_size
            pool_timeout=30,        # Timeout for getting connection from pool
            pool_recycle=3600,      # Recycle connections every hour
            pool_pre_ping=True,     # Validate connections before use
            connect_args={
                "connect_timeout": 10,
                "application_name": "pulsecheck-backend"
            }
        )
        
        SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=engine,
            expire_on_commit=False  # Prevent lazy loading issues
        )
        
        logger.info("✅ Optimized database engine initialized successfully")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database engine: {e}")
        # Create emergency SQLite engine to prevent crashes
        engine = create_engine(
            "sqlite:///./emergency.db",
            echo=False,
            pool_timeout=30,
            pool_recycle=3600
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.warning("⚠️  Using emergency SQLite database")
        return engine

def get_db() -> Session:
    """Optimized dependency to get SQLAlchemy database session"""
    global SessionLocal
    
    if SessionLocal is None:
        create_optimized_engine()
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Initialize engine on module import for better startup performance
try:
    create_optimized_engine()
except Exception as e:
    logger.warning(f"Failed to pre-initialize database engine: {e}")

# Performance monitoring functions
def get_connection_stats() -> dict:
    """Get database connection pool statistics"""
    if engine is None:
        return {"status": "not_initialized"}
    
    try:
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow()
        }
    except Exception as e:
        return {"error": str(e)} 