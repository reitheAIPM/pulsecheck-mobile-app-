from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Basic app configuration
    APP_NAME: str = "PulseCheck API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database Configuration (Supabase)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase JWT Secret for token validation - CRITICAL for security
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Legacy property names for backward compatibility
    @property
    def supabase_url(self) -> str:
        return self.SUPABASE_URL
    
    @property 
    def supabase_anon_key(self) -> str:
        return self.SUPABASE_ANON_KEY
    
    @property
    def supabase_service_key(self) -> str:
        return self.SUPABASE_SERVICE_ROLE_KEY
    
    @property
    def supabase_jwt_secret(self) -> str:
        return self.SUPABASE_JWT_SECRET
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # CORS Configuration - PRODUCTION READY
    ALLOWED_ORIGINS: list = [
        "https://pulsecheck-mobile-2objhn451-reitheaipms-projects.vercel.app",
        "https://pulse-check.vercel.app",
        "https://pulsecheck-web.vercel.app",
        "https://pulsecheck-app.vercel.app",
        "https://pulsecheck-mobile.vercel.app"
    ]
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    # Observability and Monitoring (AI-optimized)
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    JAEGER_ENDPOINT: Optional[str] = os.getenv("JAEGER_ENDPOINT")
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AI Debugging Configuration
    AI_DEBUG_MODE: bool = os.getenv("AI_DEBUG_MODE", "true").lower() == "true"
    REQUEST_CORRELATION_ENABLED: bool = os.getenv("REQUEST_CORRELATION_ENABLED", "true").lower() == "true"
    PERFORMANCE_MONITORING_ENABLED: bool = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
    USER_JOURNEY_TRACKING_ENABLED: bool = os.getenv("USER_JOURNEY_TRACKING_ENABLED", "true").lower() == "true"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS]
    
    def validate_required_settings(self):
        """Validate that required settings are configured"""
        missing_settings = []
        
        if not self.SUPABASE_URL:
            missing_settings.append("SUPABASE_URL")
        
        if not self.SUPABASE_ANON_KEY:
            missing_settings.append("SUPABASE_ANON_KEY")
        
        # JWT secret is critical for production
        if self.ENVIRONMENT == "production" and not self.supabase_jwt_secret:
            missing_settings.append("SUPABASE_JWT_SECRET")
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables that aren't defined in the model

# Global settings instance
settings = Settings()

# Validate on import
try:
    settings.validate_required_settings()
except ValueError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Configuration validation failed: {e}")
    # Don't raise in development to allow for gradual setup 