# Developer Guide 👨‍💻
*Complete Development Documentation for PulseCheck*  
*Last Updated: January 31, 2025*

## 🎯 **Developer Overview**

PulseCheck is a production-ready AI-powered wellness journaling platform with:
- **Tech Stack**: FastAPI + React + React Native + OpenAI + Supabase
- **Architecture**: RESTful API with WebSocket streaming
- **Status**: Production deployed with 99.9% uptime
- **Performance**: 2-3 second AI response times

---

## 📋 **API Documentation**

### **Base URL**
```
Production: https://pulsecheck-mobile-app-production.up.railway.app
Development: http://localhost:8000
```

### **Authentication**
All API endpoints require JWT authentication:
```bash
Authorization: Bearer <supabase_jwt_token>
```

### **Core Journal Endpoints**

#### **Create Journal Entry**
```bash
POST /api/v1/journal/entries
Content-Type: application/json

{
  "content": "My journal entry content",
  "mood_level": 7,
  "energy_level": 6,
  "stress_level": 4,
  "topics": ["work", "wellness"]
}
```

#### **Get Journal Entries**
```bash
GET /api/v1/journal/entries?page=1&per_page=30
```

#### **Get Single Entry**
```bash
GET /api/v1/journal/entries/{entry_id}
```

#### **Update Entry**
```bash
PUT /api/v1/journal/entries/{entry_id}
Content-Type: application/json

{
  "content": "Updated content",
  "mood_level": 8
}
```

#### **Delete Entry**
```bash
DELETE /api/v1/journal/entries/{entry_id}
```

### **AI Response Endpoints**

#### **Get All AI Insights for Entry**
```bash
GET /api/v1/journal/entries/{entry_id}/all-ai-insights
```

**Response:**
```json
[
  {
    "id": "uuid",
    "persona_used": "pulse",
    "ai_response": "AI response text",
    "confidence_score": 0.85,
    "topic_flags": ["wellness", "work"],
    "created_at": "2025-01-31T10:00:00Z"
  }
]
```

#### **Get Entries with AI Insights**
```bash
GET /api/v1/journal/all-entries-with-ai-insights?page=1&per_page=30
```

#### **Enhanced AI Response** (Optional features)
```bash
POST /api/v1/journal/entries/{entry_id}/adaptive-response
Content-Type: application/json

{
  "structured": true,
  "multi_persona": true,
  "streaming": false
}
```

### **Conversation Endpoints**

#### **Reply to AI Response**
```bash
POST /api/v1/journal/entries/{entry_id}/reply
Content-Type: application/json

{
  "reply_text": "Thanks for the insight!",
  "ai_insight_id": "uuid"
}
```

#### **Get Conversation Thread**
```bash
GET /api/v1/journal/entries/{entry_id}/replies
```

### **Monitoring & Debug Endpoints**

#### **Health Check**
```bash
GET /health
```

#### **Comprehensive Monitoring**
```bash
GET /api/v1/comprehensive-monitoring/quick-health-check
```

#### **AI Diagnostic**
```bash
GET /api/v1/debug/ai-diagnostic/{user_id}
```

#### **Configuration Validation**
```bash
GET /api/v1/config-validation/comprehensive
```

### **Advanced Features**

#### **WebSocket Streaming**
```javascript
const ws = new WebSocket('wss://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/entries/{entry_id}/stream');
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  // Handle streaming AI response
};
```

#### **Multi-Persona Processing**
```bash
POST /api/v1/journal/entries/{entry_id}/adaptive-response?multi_persona=true
```

---

## 🏗️ **Architecture Overview**

### **Backend Structure**
```
backend/
├── app/
│   ├── routers/           # API endpoints
│   │   ├── journal.py     # Journal operations
│   │   ├── adaptive_ai.py # Enhanced AI features
│   │   ├── admin_monitoring.py # System monitoring
│   │   └── auth.py        # Authentication
│   ├── services/          # Business logic
│   │   ├── pulse_ai_service.py # Core AI
│   │   ├── adaptive_ai_service.py # Smart AI
│   │   ├── structured_ai_service.py # Enhanced AI
│   │   └── streaming_ai_service.py # Real-time AI
│   ├── models/            # Data models
│   │   ├── journal.py     # Journal models
│   │   ├── ai_insights.py # AI response models
│   │   └── user.py        # User models
│   └── core/              # Core utilities
│       ├── database.py    # Database connection
│       ├── security.py    # Auth & validation
│       └── utils.py       # Common utilities
```

### **Database Schema**
```sql
-- Core Tables
journal_entries (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  content TEXT NOT NULL,
  mood_level INTEGER CHECK (mood_level >= 1 AND mood_level <= 10),
  energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
  stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
  topics TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ai_insights (
  id UUID PRIMARY KEY,
  journal_entry_id UUID REFERENCES journal_entries(id),
  persona_used TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  confidence_score DECIMAL(3,2),
  topic_flags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ai_user_replies (
  id UUID PRIMARY KEY,
  journal_entry_id UUID REFERENCES journal_entries(id),
  ai_insight_id UUID REFERENCES ai_insights(id),
  user_id UUID REFERENCES auth.users(id),
  reply_text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ai_reactions (
  id UUID PRIMARY KEY,
  journal_entry_id UUID REFERENCES journal_entries(id),
  ai_insight_id UUID REFERENCES ai_insights(id),
  user_id UUID REFERENCES auth.users(id),
  reaction_type TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🛠️ **Development Best Practices**

### **FastAPI + Supabase Patterns**

#### **✅ DO: Use Centralized Utilities**
```python
from app.core.utils import DateTimeUtils

# Instead of repeating this pattern:
if 'updated_at' not in entry or entry['updated_at'] is None:
    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))

# Use this:
entry = DateTimeUtils.ensure_updated_at(entry)
```

#### **✅ DO: Proper Database Client Usage**
```python
from app.core.database import get_database

# Service role for AI operations (bypasses RLS)
service_client = db.get_service_client()

# Anon client for user operations (enforces RLS)
anon_client = db.get_anon_client()
```

#### **✅ DO: Consistent Error Handling**
```python
from app.core.utils import APIResponseFormatter

try:
    result = await some_operation()
    return APIResponseFormatter.success(result)
except Exception as e:
    return APIResponseFormatter.error(str(e), 500)
```

#### **❌ DON'T: Use Unsupported Supabase Parameters**
```python
# DON'T - head=True is not supported
result = client.table("entries").select("*").head=True

# DO - Use proper pagination
result = client.table("entries").select("*").limit(1)
```

### **Environment Variables**
```python
import os
from typing import Optional

class Settings:
    # Required for production
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Optional for development
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
```

### **Testing Patterns**

#### **Unit Tests**
```python
import pytest
from app.services.pulse_ai_service import PulseAIService

def test_ai_response_generation():
    service = PulseAIService()
    entry = {
        "content": "Test journal entry",
        "mood_level": 7,
        "energy_level": 6,
        "stress_level": 4
    }
    
    response = service.generate_response(entry)
    assert response is not None
    assert len(response) > 0
```

#### **Integration Tests**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_journal_entry():
    response = client.post("/api/v1/journal/entries", json={
        "content": "Test entry",
        "mood_level": 7
    })
    assert response.status_code == 201
    assert "id" in response.json()
```

---

## 🚀 **Deployment Guide**

### **Railway Deployment (Backend)**
```bash
# Automatic deployment via git push
git add .
git commit -m "Deploy backend updates"
git push origin main

# Manual deployment (if needed)
railway up
```

### **Vercel Deployment (Frontend)**
```bash
# Automatic deployment via git push
git add .
git commit -m "Deploy frontend updates"
git push origin main

# Manual deployment (if needed)
vercel --prod
```

### **Environment Variables Setup**

#### **Railway (Backend)**
```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://...
```

#### **Vercel (Frontend)**
```bash
REACT_APP_SUPABASE_URL=https://...
REACT_APP_SUPABASE_ANON_KEY=eyJ...
REACT_APP_API_URL=https://pulsecheck-mobile-app-production.up.railway.app
```

---

## 🔍 **Debugging & Troubleshooting**

### **Common Issues & Solutions**

#### **AI Not Responding**
```bash
# Check OpenAI API key
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-diagnostic/{user_id}

# Verify scheduler status
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status

# Database client validation
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/client-validation
```

#### **Database Connection Issues**
```python
# Test connection
from app.core.database import get_database
db = get_database()
client = db.get_anon_client()
result = client.table("journal_entries").select("count").execute()
```

#### **CORS Issues**
```python
# Check CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

### **Performance Optimization**

#### **Database Queries**
```python
# Efficient pagination
def get_entries_paginated(page: int, per_page: int):
    offset = (page - 1) * per_page
    return client.table("journal_entries")\
        .select("*")\
        .range(offset, offset + per_page - 1)\
        .execute()
```

#### **AI Response Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_ai_response(entry_content: str, persona: str):
    # Cache AI responses for duplicate content
    return ai_service.generate_response(entry_content, persona)
```

---

## 📈 **Performance Metrics**

### **Target Metrics**
- **API Response Time**: <200ms
- **AI Response Time**: <3 seconds
- **Database Query Time**: <100ms
- **Frontend Load Time**: <2 seconds
- **Error Rate**: <0.1%

### **Monitoring Tools**
```bash
# Health check
curl https://pulsecheck-mobile-app-production.up.railway.app/health

# Comprehensive monitoring
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/comprehensive-monitoring/quick-health-check

# Performance metrics
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/performance-metrics
```

---

## 🤝 **Contributing Guidelines**

### **Development Workflow**
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Develop with tests**: Write tests for new functionality
4. **Run quality checks**: `python -m pytest` and `npm test`
5. **Submit PR**: Include description and test coverage

### **Code Standards**
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode, explicit types
- **Error Handling**: Comprehensive try/catch blocks
- **Documentation**: Clear docstrings and comments
- **Testing**: Unit tests for all new features

### **Pull Request Requirements**
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Performance impact considered
- [ ] Security implications reviewed

---

## 🔐 **Security Guidelines**

### **Authentication**
```python
from app.core.security import get_current_user

@router.get("/protected-endpoint")
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    # User is authenticated
    return {"user_id": current_user["id"]}
```

### **Input Validation**
```python
from pydantic import BaseModel, validator

class JournalEntryRequest(BaseModel):
    content: str
    mood_level: int
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) < 1 or len(v) > 5000:
            raise ValueError('Content must be 1-5000 characters')
        return v
```

### **Rate Limiting**
```python
from app.core.security import limiter

@router.post("/api/v1/journal/entries")
@limiter.limit("10/minute")
async def create_entry(request: Request):
    # Rate limited endpoint
    pass
```

---

## 📚 **Additional Resources**

### **Documentation Links**
- [AI System Guide](./AI-SYSTEM-GUIDE.md) - Complete AI documentation
- [Project Guide](./PROJECT-GUIDE.md) - Setup and deployment
- [API Documentation](./backend/API_DOCUMENTATION.md) - Complete API reference
- [Best Practices](./backend/FASTAPI_SUPABASE_BEST_PRACTICES.md) - Development guidelines

### **External Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Railway Documentation](https://docs.railway.app/)

---

**🎯 Bottom Line**: PulseCheck provides a robust, scalable platform for AI-powered wellness journaling with comprehensive developer tools, clear documentation, and production-ready infrastructure. 