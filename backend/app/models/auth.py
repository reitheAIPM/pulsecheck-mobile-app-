from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    expires_at: Optional[datetime] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str 