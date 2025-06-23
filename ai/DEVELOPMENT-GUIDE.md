# Development Guide - PulseCheck Project

**Purpose**: Comprehensive development setup and workflow guide for AI assistance  
**Last Updated**: January 27, 2025  
**Status**: Development ready - awaiting crisis resolution

---

## 🚀 **QUICK START DEVELOPMENT**

### **1. Initial Setup**
```bash
# Clone and setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env with your Supabase credentials

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Setup frontend in new terminal
cd spark-realm
npm install
npm run dev  # Starts both Expo and Builder Dev Tools
```

### **2. Verify Setup**
- Backend: `http://localhost:8000/health` should return 200 OK
- Frontend: `http://localhost:19006` should show React app
- Builder Tools: `http://localhost:1234` should show Builder.io dev interface

### **3. Crisis Recovery Commands** (If needed)
```bash
# Test critical endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/journal/test

# Check imports and dependencies
cd backend
python -c "from app.routers import journal; print('Success')"
python -c "from app.core.database import get_database; print('DB OK')"
```

---

## 🏗️ **FRONTEND ARCHITECTURE**

### **Tech Stack**
- **Framework**: React with TypeScript (converting to React Native)
- **Build Tool**: Vite for fast development  
- **UI Library**: Shadcn/ui with Tailwind CSS
- **Navigation**: React Router v6 (converting to React Navigation)
- **State Management**: React Context + AsyncStorage for persistence
- **Builder Integration**: Builder.io for visual editing

### **Project Structure**
```
spark-realm/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Shadcn/ui components
│   │   ├── common/         # Custom shared components
│   │   └── builder/        # Builder.io registered components
│   ├── pages/              # Page components (React Router)
│   ├── services/           # API and external services
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── types/              # TypeScript type definitions
│   └── utils/              # Helper functions
├── builder-registry.ts     # Builder.io component registry
└── vite.config.ts         # Vite configuration
```

### **Key Components**

#### **Navigation Component**
```typescript
// src/components/BottomNav.tsx
import { NavLink } from 'react-router-dom';

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
      <div className="flex justify-around py-2">
        <NavLink to="/" className={({ isActive }) => 
          isActive ? 'text-blue-600' : 'text-gray-600'
        }>
          Home
        </NavLink>
        <NavLink to="/journal" className={({ isActive }) => 
          isActive ? 'text-blue-600' : 'text-gray-600'
        }>
          Journal
        </NavLink>
        <NavLink to="/insights" className={({ isActive }) => 
          isActive ? 'text-blue-600' : 'text-gray-600'
        }>
          Insights
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => 
          isActive ? 'text-blue-600' : 'text-gray-600'
        }>
          Profile
        </NavLink>
      </div>
    </nav>
  );
}
```

#### **Error Boundary Component**
```typescript
// src/components/ErrorBoundary.tsx
import React, { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    // AI debugging context
    const aiContext = {
      componentStack: errorInfo.componentStack,
      errorBoundary: true,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    // Send to error tracking service
    this.reportError(error, aiContext);
  }

  private reportError(error: Error, context: any) {
    // Implementation for error reporting
    console.log('Reporting error with AI context:', { error, context });
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We've been notified and are working on a fix
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 🎨 **BUILDER.IO INTEGRATION**

### **Setup Configuration**

#### **1. Environment Variables**
```bash
# spark-realm/.env
VITE_BUILDER_API_KEY=your_builder_api_key_here
```

#### **2. Builder Registry**
```typescript
// builder-registry.ts
import { Builder } from '@builder.io/react';

// Initialize Builder
Builder.init(import.meta.env.VITE_BUILDER_API_KEY);

// Register custom components
import { MoodTracker } from './src/components/MoodTracker';
import { JournalCard } from './src/components/JournalCard';

Builder.registerComponent(MoodTracker, {
  name: 'MoodTracker',
  inputs: [
    { name: 'title', type: 'string', defaultValue: 'How are you feeling?' },
    { name: 'currentMood', type: 'number', defaultValue: 5 }
  ]
});

Builder.registerComponent(JournalCard, {
  name: 'JournalCard',
  inputs: [
    { name: 'date', type: 'date' },
    { name: 'content', type: 'text' },
    { name: 'moodLevel', type: 'number' }
  ]
});
```

#### **3. Development Scripts**
```json
// package.json
{
  "scripts": {
    "dev": "concurrently \"vite\" \"builder-dev-tools\"",
    "dev:vite": "vite",
    "dev:builder": "builder-dev-tools",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

### **Builder Development Workflow**

#### **1. Component Development**
1. **Create Component**: Develop in `src/components/`
2. **Register with Builder**: Add to `builder-registry.ts`
3. **Define Inputs**: Specify configurable properties
4. **Test in Builder**: Use visual editor at `localhost:1234`
5. **Export Code**: Generate optimized React code

#### **2. Figma Integration**
1. **Install Builder Plugin**: Add to Figma workspace
2. **Select Designs**: Choose components/layouts in Figma
3. **Import to Builder**: Use plugin to transfer designs
4. **Map Components**: Connect Figma elements to React components
5. **Customize**: Use Builder visual editor for adjustments

---

## 🧪 **TESTING STRATEGY**

### **Frontend Testing Setup**

#### **1. Testing Dependencies**
```json
// package.json
{
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3",
    "vitest": "^0.34.0",
    "jsdom": "^22.1.0"
  }
}
```

#### **2. Vitest Configuration**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    globals: true
  }
});
```

#### **3. Test Setup File**
```typescript
// src/test-setup.ts
import '@testing-library/jest-dom';

// Mock Builder.io
vi.mock('@builder.io/react', () => ({
  Builder: {
    init: vi.fn(),
    registerComponent: vi.fn()
  },
  BuilderComponent: vi.fn(() => null)
}));

// Mock API service
vi.mock('./services/api', () => ({
  default: {
    getJournalStats: vi.fn(),
    getJournalEntries: vi.fn(),
    createJournalEntry: vi.fn()
  }
}));
```

### **Testing Patterns**

#### **Component Testing**
```typescript
// src/components/__tests__/MoodTracker.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MoodTracker } from '../MoodTracker';

describe('MoodTracker', () => {
  it('renders with default props', () => {
    render(<MoodTracker />);
    expect(screen.getByText('How are you feeling?')).toBeInTheDocument();
  });

  it('calls onMoodChange when mood is selected', () => {
    const onMoodChange = vi.fn();
    render(<MoodTracker onMoodChange={onMoodChange} />);
    
    fireEvent.click(screen.getByText('7'));
    expect(onMoodChange).toHaveBeenCalledWith(7);
  });

  it('displays current mood selection', () => {
    render(<MoodTracker currentMood={8} />);
    const mood8Button = screen.getByText('8');
    expect(mood8Button).toHaveClass('selected'); // Assuming CSS class
  });
});
```

#### **API Service Testing**
```typescript
// src/services/__tests__/api.test.ts
import apiService from '../api';
import { vi } from 'vitest';

// Mock fetch
global.fetch = vi.fn();

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates journal entry successfully', async () => {
    const mockResponse = {
      success: true,
      data: { id: '123', content: 'Test entry' }
    };

    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const result = await apiService.createJournalEntry({
      content: 'Test entry',
      mood_level: 7,
      energy_level: 6,
      stress_level: 4
    });

    expect(result).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/journal/entries'),
      expect.objectContaining({
        method: 'POST',
        body: expect.any(String)
      })
    );
  });
});
```

### **Testing Commands**
```bash
# Run all tests
npm test

# Watch mode for development
npm run test:watch

# Coverage report
npm run test:coverage

# Type checking
npm run type-check
```

---

## 🔧 **BACKEND DEVELOPMENT**

### **FastAPI Structure**
```
backend/
├── app/
│   ├── core/              # Configuration and shared utilities
│   │   ├── config.py      # Environment configuration
│   │   ├── database.py    # Database connection
│   │   └── monitoring.py  # Error tracking and debugging
│   ├── models/            # Pydantic models and database schemas
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── journal.py     # Journal CRUD operations (CURRENTLY BROKEN)
│   │   ├── adaptive_ai.py # AI persona system
│   │   └── admin.py       # Admin analytics
│   ├── services/          # Business logic
│   │   ├── auth_service.py
│   │   ├── journal_service.py
│   │   └── adaptive_ai_service.py
│   └── utils/             # Helper functions
├── main.py               # FastAPI application entry
├── requirements.txt      # Python dependencies
└── test_deployment.py    # Production testing script
```

### **Development Commands**
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python -m pytest

# Check imports
python -c "from app.routers import journal; print('Success')"

# Test production endpoints
python test_deployment.py
```

### **Environment Configuration**
```bash
# backend/.env
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
OPENAI_API_KEY=  # Intentionally blank for MVP
```

---

## 🚨 **CRISIS DEBUGGING WORKFLOW**

### **1. Router Import Issues (Current Crisis)**
```bash
# Test router imports individually
cd backend
python -c "from app.routers.journal import router; print('Journal router OK')"
python -c "from app.routers.auth import router; print('Auth router OK')"
python -c "from app.routers.adaptive_ai import router; print('AI router OK')"

# Test service dependencies
python -c "from app.services.auth_service import get_current_user; print('Auth service OK')"
python -c "from app.core.database import get_database; print('Database OK')"
```

### **2. Endpoint Health Testing**
```bash
# Test working endpoints
curl http://localhost:8000/health
curl http://localhost:8000/

# Test broken endpoints
curl http://localhost:8000/api/v1/journal/test
curl -X POST http://localhost:8000/api/v1/journal/entries \
  -H "Content-Type: application/json" \
  -d '{"content":"test","mood_level":5,"energy_level":5,"stress_level":5}'
```

### **3. Railway Deployment Debugging**
```bash
# Check Railway logs
railway logs --tail 100

# Check deployment status
railway status

# Force redeploy
git push origin main  # Triggers automatic deployment
```

---

## 📱 **REACT NATIVE CONVERSION (PLANNED)**

### **Migration Strategy**
1. **Phase 1**: Convert core components to React Native compatible
2. **Phase 2**: Replace React Router with React Navigation
3. **Phase 3**: Implement native features (push notifications, offline sync)
4. **Phase 4**: Deploy to TestFlight for iOS beta testing

### **Key Changes Required**
- Replace `div`, `span` with `View`, `Text`
- Convert CSS styles to StyleSheet
- Replace React Router with React Navigation
- Implement AsyncStorage for offline persistence
- Add native error boundaries and crash reporting

### **Navigation Structure (React Native)**
```typescript
// Future React Navigation structure
AppNavigator (Root)
├── AuthStack
│   ├── LoginScreen
│   └── RegisterScreen
└── MainTabs
    ├── HomeStack
    ├── JournalStack
    ├── InsightsStack
    └── ProfileStack
```

---

## 🛠️ **DEVELOPMENT BEST PRACTICES**

### **Code Quality Standards**
- **TypeScript**: Strict mode enabled for both frontend and backend
- **ESLint**: Configured for React and FastAPI patterns
- **Prettier**: Consistent code formatting
- **Git Hooks**: Pre-commit hooks for quality checks

### **Performance Optimization**
- **Frontend**: React.memo for expensive components, lazy loading
- **Backend**: Async/await patterns, database query optimization
- **Caching**: Redis for session management (future implementation)
- **Monitoring**: Real-time performance metrics and error tracking

### **Error Handling Patterns**
- **Frontend**: Error boundaries with AI debugging context
- **Backend**: Comprehensive exception handling with detailed logging
- **API**: Consistent error response format across all endpoints
- **Monitoring**: Automated error detection and alerting

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **Common Frontend Issues**
1. **Build Errors**: Clear node_modules and reinstall
2. **Builder.io Issues**: Check API key configuration
3. **Route Not Found**: Verify React Router setup
4. **TypeScript Errors**: Run type checking and fix issues

### **Common Backend Issues**
1. **Import Errors**: Check Python path and dependencies
2. **Database Connection**: Verify Supabase credentials
3. **Router 404s**: Check router registration in main.py
4. **Authentication Issues**: Verify JWT token handling

### **Development Environment Reset**
```bash
# Frontend reset
cd spark-realm
rm -rf node_modules package-lock.json
npm install
npm run dev

# Backend reset
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

**This file consolidates: development-setup-guide.md, consolidated-frontend-guide.md, builder-integration-guide.md** 