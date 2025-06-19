# PulseCheck Development Setup Guide

*Complete setup guide for PulseCheck development environment with all tools and best practices*

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.11+)
- **Git**
- **Expo CLI**: `npm install -g @expo/cli`
- **Builder.io Account**: [Sign up here](https://builder.io)
- **Supabase Account**: [Sign up here](https://supabase.com)
- **OpenAI API Key**: [Get here](https://platform.openai.com)

### One-Command Setup
```bash
# Clone and setup everything
git clone <repository-url>
cd pulsecheck
./scripts/setup-dev.sh  # Coming soon
```

---

## 🔧 Backend Setup

### 1. Environment Configuration
```bash
cd backend
cp env.example .env
```

Edit `.env` with your credentials:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

### 2. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create database schema
python create_database_schema.py

# Run offline tests
python test_backend_offline_complete.py
```

### 4. Start Backend Server
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the script
python -m uvicorn main:app --reload
```

**Backend will be available at**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/docs`

---

## 📱 Frontend Setup

### 1. Environment Configuration
```bash
cd frontend
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# API Configuration
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1

# Builder.io Configuration
EXPO_PUBLIC_BUILDER_API_KEY=your-builder-api-key

# Development Configuration
EXPO_PUBLIC_ENVIRONMENT=development
```

### 2. Install Dependencies
```bash
npm install

# Install Builder.io dependencies
npm install --save-dev @builder.io/react @builder.io/dev-tools concurrently
```

### 3. Update Package.json Scripts
```json
{
  "scripts": {
    "start": "expo start",
    "dev": "concurrently \"expo start\" \"builder-dev-tools\"",
    "dev:builder": "builder-dev-tools",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "test": "jest",
    "type-check": "tsc --noEmit",
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix"
  }
}
```

### 4. Builder.io Configuration
Create `builder-registry.ts`:
```typescript
import { Builder } from '@builder.io/react';
import { BUILDER_CONFIG } from './src/constants/config';

// Import your components
import { CheckinForm } from './src/components/checkin/CheckinForm';
import { MoodCard } from './src/components/common/MoodCard';

// Register components
Builder.registerComponent(CheckinForm, {
  name: 'CheckinForm',
  inputs: [
    { name: 'title', type: 'string', defaultValue: 'How are you feeling?' },
    { name: 'showJournal', type: 'boolean', defaultValue: true }
  ]
});

Builder.registerComponent(MoodCard, {
  name: 'MoodCard',
  inputs: [
    { name: 'moodScore', type: 'number', defaultValue: 7 },
    { name: 'date', type: 'date' }
  ]
});

// Initialize Builder
Builder.init(BUILDER_CONFIG.apiKey);
```

### 5. Start Frontend Development
```bash
# Start both Expo and Builder Dev Tools
npm run dev

# Or start individually
npm start          # Expo only
npm run dev:builder # Builder Dev Tools only
```

**Frontend will be available at**: `http://localhost:19006`
**Builder Dev Tools**: `http://localhost:1234`

---

## 🧪 Testing Setup

### Backend Testing
```bash
cd backend

# Run all tests
python test_backend_offline_complete.py

# Run specific test categories
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run type checking
npm run type-check

# Run linting
npm run lint
```

---

## 🔗 Integration Testing

### 1. API Connection Test
```bash
# Test backend health
curl http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/api/v1/checkins
```

### 2. Frontend-Backend Integration
```bash
# Start both servers
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 3. Builder.io Integration Test
1. Open Builder.io dashboard
2. Create a new page with "figma-imports" model
3. Add components from your registry
4. Preview in your app at `http://localhost:19006`

---

## 🛠️ Development Workflow

### Daily Development Process
```bash
# 1. Start development environment
cd backend && uvicorn main:app --reload &
cd frontend && npm run dev &

# 2. Make changes
# - Backend: Edit Python files, auto-reload
# - Frontend: Edit React Native files, auto-reload
# - Builder: Use Visual Editor for UI changes

# 3. Test changes
cd backend && python test_backend_offline_complete.py
cd frontend && npm test

# 4. Commit changes
git add .
git commit -m "feat: add new feature"
```

### Component Development Workflow
1. **Design in Figma**: Create component designs
2. **Import to Builder**: Use Builder Figma plugin
3. **Map Components**: Connect to React Native code
4. **Register Components**: Add to builder-registry.ts
5. **Test Integration**: Verify in app
6. **Iterate**: Use Builder Visual Editor

### API Development Workflow
1. **Define Models**: Update Pydantic models
2. **Create Services**: Add business logic
3. **Add Routes**: Create API endpoints
4. **Update Tests**: Add comprehensive tests
5. **Update Docs**: Update api-endpoints.md
6. **Test Integration**: Verify with frontend

---

## 🔍 Troubleshooting

### Common Backend Issues

#### Database Connection Errors
```bash
# Check Supabase credentials
python -c "from app.core.database import get_database_url; print(get_database_url())"

# Test connection manually
python -c "from app.core.database import get_db; print('Connection OK')"
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn main:app --reload --port 8001
```

### Common Frontend Issues

#### Builder.io Connection Errors
```bash
# Check API key
echo $EXPO_PUBLIC_BUILDER_API_KEY

# Verify Builder configuration
npm run type-check
```

#### Navigation Errors
```typescript
// Ensure single NavigationContainer
// Check navigation types
// Verify screen names match
```

#### Expo Issues
```bash
# Clear cache
expo start --clear

# Reset Metro bundler
npx expo start --clear

# Check Expo CLI version
expo --version
```

---

## 📚 Best Practices Checklist

### Backend
- ✅ Virtual environment activated
- ✅ All dependencies installed
- ✅ Environment variables configured
- ✅ Database schema created
- ✅ Offline tests passing
- ✅ API documentation accessible

### Frontend
- ✅ Node modules installed
- ✅ Environment variables configured
- ✅ Builder.io API key set
- ✅ Component registry created
- ✅ Navigation types defined
- ✅ TypeScript compilation successful

### Integration
- ✅ Backend server running
- ✅ Frontend development server running
- ✅ Builder Dev Tools accessible
- ✅ API endpoints responding
- ✅ Frontend connecting to backend
- ✅ Builder.io components loading

### Development Tools
- ✅ Git repository initialized
- ✅ ESLint configured
- ✅ Prettier configured
- ✅ Jest testing setup
- ✅ TypeScript strict mode
- ✅ Pre-commit hooks (optional)

---

## 🚀 Next Steps

After completing setup:

1. **Explore the API**: Visit `http://localhost:8000/docs`
2. **Test the App**: Open `http://localhost:19006`
3. **Try Builder.io**: Visit `http://localhost:1234`
4. **Read Documentation**: Review `ai/` folder
5. **Start Developing**: Follow the development workflow

### Recommended First Tasks
1. Create a test user account
2. Submit a test check-in
3. View the check-in in the app
4. Try the Builder.io visual editor
5. Add a custom component

---

*This guide should be updated as the project evolves and new tools are added.* 