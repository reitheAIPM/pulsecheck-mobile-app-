"""
Common Models
Shared Pydantic models used across the application
"""

from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from datetime import datetime

class StandardResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

class ErrorResponse(BaseModel):
    """Standard error response format"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

class HealthCheckResponse(BaseModel):
    """Health check response format"""
    status: str  # "healthy", "degraded", "unhealthy"
    version: Optional[str] = None
    timestamp: datetime
    services: Optional[Dict[str, str]] = None
    uptime_seconds: Optional[float] = None

class PaginatedResponse(BaseModel):
    """Paginated response format"""
    items: List[Any]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool 