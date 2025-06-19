# PulseCheck - API Endpoints & Development Reference

*Comprehensive technical documentation for backend API, development processes, and common tasks*

---

## 📋 Development Process Guidelines

### Project Status & Structure
- **Current Phase**: Foundation Complete - Core Feature Development
- **Backend**: FastAPI (Python) with Supabase PostgreSQL
- **Frontend**: React Native (Expo) with TypeScript + Builder.io integration
- **Navigation**: React Navigation v6 with type-safe routing
- **AI Integration**: OpenAI GPT-4 for consistent personality
- **Design System**: Builder.io for visual editing and component management

### File Organization Standards
```
backend/
├── app/
│   ├── core/          # Configuration, database, security
│   ├── models/        # Pydantic models & SQLAlchemy schemas
│   ├── routers/       # API route handlers
│   ├── services/      # Business logic
│   └── utils/         # Helper functions
├── tests/             # Test files
├── main.py           # FastAPI application entry
└── requirements.txt  # Dependencies

frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Shared components (Button, Input, etc.)
│   │   ├── screens/        # Screen-specific components
│   │   └── builder/        # Builder.io registered components
│   ├── screens/            # Screen components
│   ├── navigation/         # Navigation configuration
│   ├── services/           # API and external services
│   ├── hooks/              # Custom React hooks
│   ├── context/            # React Context providers
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Helper functions
│   └── constants/          # App constants and config
├── assets/                 # Images, fonts, etc.
├── builder-registry.ts     # Builder.io component registry
└── app.json               # Expo configuration
```

### Common Development Tasks

#### Starting Development Environment
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python setup_dev_env.py  # Validates environment
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend  
npm install
npm run dev  # Runs Expo + Builder Dev Tools concurrently
```

#### Database Operations
- **Connection**: Managed via `app/core/database.py`
- **Migrations**: Use Supabase dashboard or SQL migrations
- **Environment**: Configure via `.env` file (see `env.example`)
- **Testing**: Use `test_backend_offline.py` for offline validation

#### Code Quality Standards
- **Backend**: FastAPI async/await patterns, Pydantic validation
- **Frontend**: TypeScript strict mode, React Navigation type safety
- **Error Handling**: Consistent JSON error responses (see Error Handling section)
- **Authentication**: JWT Bearer tokens for all protected endpoints
- **Validation**: All inputs validated with Pydantic models
- **Documentation**: Auto-generated with FastAPI OpenAPI

#### AI Integration Guidelines
- **Persona**: "Pulse" - warm, professional, insight-focused
- **Context**: Always include recent mood data for relevant responses
- **Response Format**: Analysis + Actionable recommendations + Reflection question
- **Rate Limiting**: Prevent AI abuse with user-based limits
- **Fallbacks**: Handle AI service failures gracefully

#### Frontend Integration Guidelines
- **Builder.io**: Use for visual editing and component management
- **Navigation**: Single NavigationContainer with type-safe routing
- **State Management**: React Context + AsyncStorage for persistence
- **Component Registry**: Register reusable components with Builder.io
- **Design Tokens**: Consistent spacing, colors, and typography

---

## 🔗 Base Configuration

**Base URL**: `https://api.pulsecheck.app/v1` (Production)  
**Dev URL**: `http://localhost:8000/api/v1` (Development)  
**Authentication**: JWT Bearer tokens  
**Rate Limiting**: 100 requests/minute per user  
**Response Format**: JSON with consistent error handling

**Frontend Dev Server**: `http://localhost:19006` (Expo)  
**Builder Dev Tools**: `http://localhost:1234` (Builder.io)  
**Builder API Key**: Configure via `EXPO_PUBLIC_BUILDER_API_KEY`

---

## 🔐 Authentication Endpoints

### POST `/auth/register`
Create new user account
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "timezone": "America/New_York"
}
```

### POST `/auth/login`
User authentication
```json
{
  "email": "user@example.com", 
  "password": "securePassword123"
}
```

### POST `/auth/refresh`
Refresh JWT token
```json
{
  "refreshToken": "jwt_refresh_token_here"
}
```

### POST `/auth/logout`
Invalidate user session
*Requires Authentication Header*

---

## 📊 Check-in & Mood Tracking

### POST `/checkins`
Submit daily check-in data
*Requires Authentication*
```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "moodScore": 7,
  "energyLevel": 6,
  "stressLevel": 4,
  "journalEntry": "Had a productive morning but feeling overwhelmed by afternoon meetings...",
  "sleepHours": 7.5,
  "workHours": 9,
  "exerciseMinutes": 30,
  "tags": ["work-stress", "productive", "meetings"]
}
```

### GET `/checkins`
Retrieve user's check-in history
*Requires Authentication*
```
Query Parameters:
- limit (default: 30)
- offset (default: 0) 
- startDate (ISO 8601)
- endDate (ISO 8601)
```

### GET `/checkins/{id}`
Get specific check-in details
*Requires Authentication*

---

## 🧠 AI Analysis & Insights

### POST `/ai/analyze`
Get AI analysis of recent mood patterns
*Requires Authentication*
```json
{
  "timeframe": "7d", // "1d", "7d", "30d"
  "includeJournal": true,
  "focusAreas": ["mood-patterns", "work-stress", "lifestyle-factors"]
}
```

**Response:**
```json
{
  "analysis": {
    "summary": "Over the past week, I notice you've reported higher stress levels on Monday and Tuesday...",
    "patterns": [
      {
        "type": "weekly-cycle",
        "description": "Stress peaks early in the week",
        "confidence": 0.85
      }
    ],
    "recommendations": [
      {
        "action": "Consider blocking 15 minutes Sunday evening for week planning",
        "rationale": "Preparation might reduce Monday morning overwhelm",
        "difficulty": "easy"
      }
    ]
  },
  "reflectionQuestion": "What's one small change you could make to your Sunday routine that might help you feel more prepared for the week ahead?"
}
```

### POST `/ai/chat`
Conversational interaction with AI coach
*Requires Authentication*
```json
{
  "message": "I'm feeling really burned out lately",
  "context": {
    "recentMoodTrend": "declining",
    "timeOfDay": "evening",
    "dayOfWeek": "Friday"
  }
}
```

---

## 📈 Progress & Analytics

### GET `/analytics/dashboard`
User's wellness dashboard data
*Requires Authentication*
```json
{
  "timeframe": "30d",
  "metrics": ["mood", "energy", "stress", "sleep"]
}
```

### GET `/analytics/streaks`
User's consistency streaks and achievements
*Requires Authentication*

### GET `/analytics/export`
Export user data (GDPR compliance)
*Requires Authentication*
```
Query Parameters:
- format: "json" | "csv"
- startDate (ISO 8601)
- endDate (ISO 8601)
```

---

## ⚙️ User Preferences & Settings

### GET `/users/profile`
Get user profile and preferences
*Requires Authentication*

### PUT `/users/profile`
Update user profile
*Requires Authentication*
```json
{
  "firstName": "John",
  "timezone": "America/Los_Angeles",
  "notificationPreferences": {
    "dailyReminder": true,
    "reminderTime": "09:00",
    "weeklyInsights": true
  },
  "privacySettings": {
    "dataRetentionDays": 365,
    "shareAnonymizedData": false
  }
}
```

### DELETE `/users/account`
Delete user account and all data
*Requires Authentication + Password Confirmation*

---

## 📱 Health Integration (Future)

### POST `/integrations/healthkit`
Connect Apple HealthKit data
*Requires Authentication*

### POST `/integrations/googlefit`
Connect Google Fit data
*Requires Authentication*

### GET `/integrations/status`
Check connected integrations status
*Requires Authentication*

---

## 🚨 Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The provided mood score must be between 1 and 10",
    "details": {
      "field": "moodScore",
      "providedValue": 15
    },
    "timestamp": "2024-01-15T14:30:00Z",
    "requestId": "req_abc123"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED` (401)
- `INVALID_TOKEN` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `VALIDATION_ERROR` (400)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_SERVER_ERROR` (500)

---

## 🔄 API Versioning Strategy

- **Current Version**: v1
- **Deprecation Policy**: 6 months notice for breaking changes
- **Backwards Compatibility**: Maintained within major versions
- **Version Header**: `API-Version: v1` (optional, defaults to latest)

---

## 🛠️ Common Troubleshooting

### Backend Issues
- **Port conflicts**: FastAPI runs on :8000, check if port is available
- **Database connection**: Verify Supabase credentials in `.env`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Import errors**: Ensure `PYTHONPATH` includes project root

### Frontend Issues
- **Builder.io connection**: Check API key in environment variables
- **Navigation errors**: Ensure single NavigationContainer at root
- **Component registration**: Verify components are registered in builder-registry.ts
- **TypeScript errors**: Run `npm run type-check` for type validation

### Development Workflow
1. **New Feature**: Create branch, implement with tests, update this file
2. **Database Changes**: Update models, create migration, test locally
3. **API Changes**: Update endpoints here, implement, test, document
4. **AI Integration**: Test with mock data first, then integrate OpenAI
5. **Frontend Components**: Design in Figma, import to Builder, register components

### Testing Strategy
- **Offline Tests**: `test_backend_offline.py` for structure validation
- **API Tests**: Test all endpoints with realistic data
- **AI Tests**: Mock OpenAI responses for consistent testing
- **Integration Tests**: End-to-end user flows
- **Frontend Tests**: Jest + React Native Testing Library

---

## 🎨 Frontend Integration Patterns

### Builder.io Component Registration
```typescript
// Register components for visual editing
Builder.registerComponent(CheckinForm, {
  name: 'CheckinForm',
  inputs: [
    { name: 'title', type: 'string', defaultValue: 'How are you feeling?' },
    { name: 'showJournal', type: 'boolean', defaultValue: true }
  ]
});
```

### Navigation Type Safety
```typescript
// Define navigation types
type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

type MainTabParamList = {
  Home: undefined;
  Checkin: undefined;
  Insights: undefined;
  Profile: undefined;
};
```

### API Client Integration
```typescript
// Typed API client with authentication
const apiClient = {
  auth: {
    login: (credentials: LoginRequest): Promise<Token> => 
      api.post('/auth/login', credentials),
    register: (userData: UserCreate): Promise<UserResponse> => 
      api.post('/auth/register', userData)
  },
  checkins: {
    create: (data: CheckInCreate): Promise<CheckInResponse> => 
      api.post('/checkins', data),
    list: (params: CheckinListParams): Promise<CheckInResponse[]> => 
      api.get('/checkins', { params })
  }
};
```

---

*This document serves as the single source of truth for PulseCheck development. Update it whenever adding new processes, endpoints, or changing existing functionality.*

**Status**: Foundation Complete - Ready for Core Feature Implementation  
**Last Updated**: Current session - Added frontend integration patterns and Builder.io workflow  
**Next Update**: After implementing database schema and first endpoints 