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
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:19006,http://localhost:5173,http://localhost:5174,https://pulsecheck-mobile-9883ycydx-reitheaipms-projects.vercel.app,https://pulsecheck-mobile-1pozgd468-reitheaipms-projects.vercel.app,https://pulsecheck-mobile-3senyo0m9-reitheaipms-projects.vercel.app,https://*.vercel.app"
    
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
        """Validate that required settings are present"""
        missing = []
        
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_anon_key:
            missing.append("SUPABASE_ANON_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
            
        if missing and self.environment == "production":
            print(f"⚠️  WARNING: Missing required environment variables in production: {', '.join(missing)}")
            print("🔧 Please set these variables in your Railway dashboard")
            # Don't fail in production, just warn
        elif missing:
            print(f"⚠️  Missing environment variables: {', '.join(missing)}")
            print("💡 These are required for full functionality")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from environment

# Global settings instance
try:
    settings = Settings()
    settings.validate_required_settings()
except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("🔧 Check your environment variables")
    # Create minimal settings for health checks
    settings = Settings(
        supabase_url="",
        supabase_anon_key="", 
        openai_api_key=""
    ) 