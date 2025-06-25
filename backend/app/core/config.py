from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    
    # Database Configuration (Supabase)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase JWT Secret for token validation - CRITICAL for security
    supabase_jwt_secret: str = ""
    
    # Rate Limiting Configuration
    rate_limit_enabled: bool = True
    rate_limit_redis_url: Optional[str] = None
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:19006,http://localhost:5173,http://localhost:5174,https://pulsecheck-mobile-9883ycydx-reitheaipms-projects.vercel.app,https://pulsecheck-mobile-1pozgd468-reitheaipms-projects.vercel.app,https://pulsecheck-mobile-3senyo0m9-reitheaipms-projects.vercel.app,https://pulsecheck-mobile-743jnmyh8-reitheaipms-projects.vercel.app"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def validate_required_settings(self):
        """Validate that required settings are configured"""
        missing_settings = []
        
        if not self.supabase_url:
            missing_settings.append("SUPABASE_URL")
        
        if not self.supabase_anon_key:
            missing_settings.append("SUPABASE_ANON_KEY")
        
        # JWT secret is critical for production
        if self.environment == "production" and not self.supabase_jwt_secret:
            missing_settings.append("SUPABASE_JWT_SECRET")
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
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