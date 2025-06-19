from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    
    # Database Configuration (Supabase)
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: str
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:19006"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 