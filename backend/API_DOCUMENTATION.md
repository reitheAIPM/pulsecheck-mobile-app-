# PulseCheck API Documentation

**Base URL:** `https://pulsecheck-mobile-app-production.up.railway.app`

## 🏥 Health Check

### Get API Health
```
GET /health
```
Returns system health status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "service": "PulseCheck Mobile API",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 📝 Journal Entries

### Create Journal Entry
```
POST /api/v1/journal/entries
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "string",
  "mood_level": 1-10,
  "energy_level": 1-10,
  "stress_level": 1-10,
  "sleep_hours": 0-24,
  "work_hours": 0-24,
  "tags": ["string"],
  "work_challenges": ["string"],
  "gratitude_items": ["string"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "content": "string",
  "mood_level": 5,
  "energy_level": 5,
  "stress_level": 5,
  "created_at": "2025-07-02T15:14:42Z",
  "updated_at": "2025-07-02T15:14:42Z",
  "ai_insights": {
    "insight": "AI response text",
    "persona_used": "pulse",
    "confidence_score": 0.7
  },
  "ai_generated_at": "2025-07-02T15:14:43Z"
}
```

### Get Journal Entries
```
GET /api/v1/journal/entries?page=1&per_page=30
```

**Response:**
```json
{
  "entries": [...], 
  "total": 50,
  "page": 1,
  "per_page": 30,
  "total_pages": 2
}
```

### Get Single Journal Entry
```
GET /api/v1/journal/entries/{entry_id}
```

### Update Journal Entry
```
PUT /api/v1/journal/entries/{entry_id}
Content-Type: application/json
```

### Delete Journal Entry
```
DELETE /api/v1/journal/entries/{entry_id}
```

---

## 🤖 AI Responses

### Get AI Response for Journal Entry
```
GET /api/v1/journal/entries/{entry_id}/pulse
```

**Response:**
```json
{
  "insight": "AI generated insight",
  "action": "Suggested action",
  "question": "Follow-up question",
  "mood_analysis": "Mood analysis"
}
```

### Get AI Insights for Journal Entry
```
GET /api/v1/journal/entries/{entry_id}/ai-insights
```

**Response:**
```json
{
  "id": "uuid",
  "journal_entry_id": "uuid",
  "ai_response": "AI response text",
  "persona_used": "pulse",
  "topic_flags": ["wellness", "work"],
  "confidence_score": 0.7,
  "created_at": "2025-07-02T15:14:43Z"
}
```

### Get All AI Insights for Journal Entry (Multi-Persona)
```
GET /api/v1/journal/entries/{entry_id}/all-ai-insights
```

**Response:**
```json
{
  "insights": [
    {
      "id": "uuid",
      "journal_entry_id": "uuid",
      "ai_response": "Pulse AI response about your energy levels...",
      "persona_used": "pulse",
      "topic_flags": ["wellness", "energy"],
      "confidence_score": 0.85,
      "created_at": "2025-07-02T15:14:43Z"
    },
    {
      "id": "uuid",
      "journal_entry_id": "uuid", 
      "ai_response": "Sage AI response providing thoughtful perspective...",
      "persona_used": "sage",
      "topic_flags": ["reflection", "wisdom"],
      "confidence_score": 0.82,
      "created_at": "2025-07-02T15:14:44Z"
    }
  ],
  "total_personas": 4,
  "personas_responded": ["pulse", "sage", "spark", "anchor"]
}
```

### Get All Journal Entries with AI Insights (Production)
```
GET /api/v1/journal/all-entries-with-ai-insights?page=1&per_page=30
```

**Response:**
```json
{
  "entries": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "content": "Journal entry content...",
      "mood_level": 7,
      "energy_level": 6,
      "stress_level": 4,
      "created_at": "2025-07-02T15:14:42Z",
      "updated_at": "2025-07-02T15:14:42Z",
      "ai_insights": [
        {
          "id": "uuid",
          "ai_response": "Pulse AI response...",
          "persona_used": "pulse",
          "topic_flags": ["wellness"],
          "confidence_score": 0.85,
          "created_at": "2025-07-02T15:14:43Z"
        },
        {
          "id": "uuid", 
          "ai_response": "Sage AI response...",
          "persona_used": "sage",
          "topic_flags": ["reflection"],
          "confidence_score": 0.82,
          "created_at": "2025-07-02T15:14:44Z"
        }
      ]
    }
  ],
  "page": 1,
  "per_page": 30,
  "total": 25
}
```

### Get All AI Responses for User (Testing Only)
```
GET /api/v1/frontend-fix/ai-responses/{user_id}
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "total_journal_entries": 6,
  "total_ai_responses": 3,
  "journal_entries": [...],
  "ai_responses": [
    {
      "id": "uuid",
      "journal_entry_id": "uuid", 
      "response": "AI response text",
      "persona": "pulse",
      "confidence": 0.7,
      "created_at": "2025-07-02T15:14:43Z",
      "source": "ai_insights"
    }
  ],
  "latest_ai_response": {...}
}
```

---

## 📊 Statistics

### Get Journal Statistics
```
GET /api/v1/journal/stats
```

**Response:**
```json
{
  "total_entries": 25,
  "current_streak": 3,
  "longest_streak": 7,
  "average_mood": 6.5,
  "average_energy": 5.8,
  "average_stress": 4.2,
  "last_entry_date": "2025-07-02",
  "mood_trend": "improving",
  "energy_trend": "stable",
  "stress_trend": "decreasing"
}
```

---

## 🛠️ Manual AI Endpoints (Testing)

### Manual AI Response for Latest Journal
```
POST /api/v1/manual-ai/respond-to-latest/{user_id}
```

### Manual AI Response for Specific Journal
```
POST /api/v1/manual-ai/respond-to-journal/{journal_id}?user_id={user_id}
```

---

## 🔍 Monitoring & Debug

### AI Monitoring Status
```
GET /api/v1/ai-monitoring/last-action/{user_id}
```

**Response:**
```json
{
  "user_id": "uuid",
  "last_journal_entry": "journal content preview...",
  "ai_flow_status": "completed",
  "last_ai_response": "AI response preview...",
  "timestamp": "2025-07-02T15:14:43Z"
}
```

---

## 📱 Frontend Integration Guide

### Mobile App (React Native)
The mobile app should use these endpoints:

1. **Create Journal:** `POST /api/v1/journal/entries`
2. **Get Entries:** `GET /api/v1/journal/entries`
3. **Get AI Response:** `GET /api/v1/journal/entries/{entry_id}/pulse`

### Web App (React)
Same endpoints as mobile app.

### Testing & Debug
Use `/api/v1/frontend-fix/ai-responses/{user_id}` for debugging AI responses without authentication.

---

## 📋 Database Tables

### Current Tables in Use:
- ✅ `journal_entries` - Main journal data
- ✅ `ai_insights` - AI responses and analysis
- ✅ `user_preferences` - User settings

### Deprecated Tables:
- ❌ `ai_comments` - (Old table, no longer used)

---

## 🚀 Rate Limits

- **Journal Creation:** 5/minute
- **AI Requests:** 10/minute  
- **General API:** 60/minute
- **Stats:** 30/minute

---

## 🔐 Authentication

Most endpoints require authentication. Test endpoints with `/api/v1/frontend-fix/` prefix bypass authentication for development.

**User ID for Testing:** `6abe6283-5dd2-46d6-995a-d876a06a55f7` 