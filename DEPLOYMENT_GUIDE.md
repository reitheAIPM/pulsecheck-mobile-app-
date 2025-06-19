# PulseCheck Deployment Guide

## 🎯 Current Status: Foundation Complete ✅

The PulseCheck MVP foundation is complete with:
- ✅ FastAPI backend with full journal API
- ✅ React Native frontend with beautiful UI
- ✅ Pulse AI integration with OpenAI
- ✅ Complete type safety and error handling

## 🚀 Next Steps: Database & Deployment

### Step 1: Supabase Database Setup

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note down your URL and anon key

2. **Create Database Tables**
   
   Run these SQL commands in Supabase SQL Editor:

   ```sql
   -- Users table
   CREATE TABLE users (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       name TEXT NOT NULL,
       tech_role TEXT NOT NULL,
       experience_years INTEGER,
       company_size TEXT,
       role TEXT DEFAULT 'user',
       is_active BOOLEAN DEFAULT true,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Journal entries table
   CREATE TABLE journal_entries (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       user_id UUID REFERENCES users(id) ON DELETE CASCADE,
       content TEXT NOT NULL,
       mood_level INTEGER NOT NULL CHECK (mood_level >= 1 AND mood_level <= 10),
       energy_level INTEGER NOT NULL CHECK (energy_level >= 1 AND energy_level <= 10),
       stress_level INTEGER NOT NULL CHECK (stress_level >= 1 AND stress_level <= 10),
       sleep_hours DECIMAL,
       work_hours DECIMAL,
       tags TEXT[] DEFAULT '{}',
       work_challenges TEXT[] DEFAULT '{}',
       gratitude_items TEXT[] DEFAULT '{}',
       ai_insights JSONB,
       ai_generated_at TIMESTAMP WITH TIME ZONE,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create demo user for testing
   INSERT INTO users (email, name, tech_role) 
   VALUES ('demo@pulsecheck.app', 'Demo User', 'developer');
   ```

### Step 2: Environment Configuration

1. **Backend Environment (.env)**
   ```bash
   cd backend
   cp env.example .env
   ```

   Edit `.env` with your keys:
   ```env
   ENVIRONMENT=development
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_generated_secret_key
   ```

2. **Generate Secret Key**
   ```bash
   # On macOS/Linux
   openssl rand -hex 32
   
   # On Windows (PowerShell)
   [System.Web.Security.Membership]::GeneratePassword(32, 0)
   ```

### Step 3: Test Backend Locally

1. **Install Python Dependencies**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Run Backend**
   ```bash
   python main.py
   ```

3. **Test API**
   - Visit `http://localhost:8000/health`
   - Check `http://localhost:8000/docs` for API documentation

### Step 4: Test Frontend

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

3. **Test on Device/Simulator**
   - Scan QR code with Expo Go app
   - Or run `npm run ios` / `npm run android`

### Step 5: Deploy Backend to Railway

1. **Create Railway Account**
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Configure Railway Environment**
   ```env
   ENVIRONMENT=production
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key
   PORT=8000
   ```

3. **Deploy**
   - Railway will auto-deploy from your repository
   - Note the deployment URL (e.g., `https://your-app.railway.app`)

### Step 6: Update Frontend API URL

1. **Update API Service**
   ```typescript
   // frontend/src/services/api.ts
   private baseURL = 'https://your-app.railway.app'; // Replace with your Railway URL
   ```

2. **Test End-to-End**
   - Create journal entry in mobile app
   - Verify it saves to Supabase
   - Test Pulse AI response generation

## 🧪 Testing Checklist

### Backend Tests
- [ ] Health check endpoint responds
- [ ] Create journal entry works
- [ ] Get journal entries works
- [ ] Get journal stats works
- [ ] Pulse AI response generates
- [ ] AI analysis endpoint works

### Frontend Tests
- [ ] Home screen loads with stats
- [ ] Journal entry screen accepts input
- [ ] Sliders work properly
- [ ] Form submission works
- [ ] Pulse response screen displays AI insights
- [ ] Navigation works between screens

### Integration Tests
- [ ] End-to-end journal creation flow
- [ ] AI response generation and display
- [ ] Error handling for network issues
- [ ] Offline behavior (graceful degradation)

## 🐛 Common Issues & Solutions

### Backend Issues

**Python not found**
- Install Python 3.8+ from python.org
- Ensure Python is in your PATH

**Package installation fails**
- Update pip: `pip install --upgrade pip`
- Use virtual environment: `python -m venv venv`

**Database connection fails**
- Check Supabase URL and key in .env
- Verify database tables are created
- Check network connectivity

**OpenAI API errors**
- Verify API key is correct
- Check OpenAI account has credits
- Ensure API key has proper permissions

### Frontend Issues

**Metro bundler fails**
- Clear cache: `npx expo start --clear`
- Delete node_modules and reinstall
- Update Expo CLI: `npm install -g @expo/cli`

**Navigation errors**
- Ensure all screen imports are correct
- Check TypeScript types match navigation params
- Verify React Navigation packages are installed

**API connection fails**
- Check backend URL in api.ts
- Verify backend is running and accessible
- Check CORS configuration

## 📊 Monitoring & Analytics

### Backend Monitoring
- Railway provides built-in metrics
- Monitor API response times
- Track error rates and types
- Watch database query performance

### Frontend Analytics
- User engagement metrics
- Screen navigation patterns
- Error tracking and crash reports
- AI response quality feedback

## 🔒 Security Checklist

### Backend Security
- [ ] Environment variables properly configured
- [ ] CORS settings appropriate for production
- [ ] Database access properly restricted
- [ ] API rate limiting implemented
- [ ] Error messages don't expose sensitive data

### Frontend Security
- [ ] API keys not exposed in client code
- [ ] Secure storage for sensitive data
- [ ] Network requests use HTTPS
- [ ] User input properly validated

## 🚀 Production Readiness

### Performance
- [ ] API response times < 500ms
- [ ] Mobile app loads < 3 seconds
- [ ] AI responses generate < 5 seconds
- [ ] Database queries optimized

### Reliability
- [ ] Error handling for all failure modes
- [ ] Graceful degradation when services unavailable
- [ ] Proper loading states and user feedback
- [ ] Offline capability where appropriate

### User Experience
- [ ] Intuitive navigation and flow
- [ ] Clear error messages and guidance
- [ ] Consistent visual design
- [ ] Accessibility standards met

---

## 🎉 Success Criteria

When deployment is complete, you should have:

1. **Working Backend**: FastAPI server running on Railway with database
2. **Mobile App**: React Native app connecting to your backend
3. **AI Integration**: Pulse providing personalized wellness insights
4. **Data Flow**: Complete journal → AI → insight loop working
5. **Monitoring**: Basic analytics and error tracking in place

Ready to help tech workers improve their wellness! 🧠💙

---

*Need help with deployment? Check the troubleshooting section or refer to the comprehensive README.md*