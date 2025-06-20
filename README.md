# PulseCheck - AI-Powered Wellness Companion

PulseCheck is an AI-powered mobile app designed to help tech workers prevent burnout through daily wellness check-ins and personalized insights from "Pulse," an emotionally intelligent AI companion.

## 🎯 Core Features

- **Daily Wellness Check-ins**: Track mood, energy, stress levels with intuitive sliders
- **Pulse AI Companion**: Get personalized insights and gentle guidance
- **Pattern Recognition**: AI analyzes trends to provide meaningful wellness insights
- **Tech Worker Focused**: Understands industry-specific stressors and challenges
- **Privacy-First**: Your wellness data stays secure

## 🏗️ Project Structure

```
PulseCheck/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── core/           # Configuration and database
│   │   ├── models/         # Pydantic data models
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic (Pulse AI)
│   ├── main.py             # FastAPI app entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # React Native (Expo) mobile app
│   ├── src/
│   │   ├── screens/        # App screens
│   │   ├── services/       # API communication
│   │   └── types/          # TypeScript types
│   └── App.tsx             # Main app component
└── ai/                     # AI documentation and guides
```

## 🚀 Quick Start

### Backend Setup (FastAPI)

1. **Install Python 3.8+**
   ```bash
   # Windows: Download from python.org
   # macOS: brew install python
   # Linux: sudo apt install python3 python3-pip
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys (see Environment Setup below)
   ```

4. **Run the backend**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup (React Native)

1. **Install Node.js 16+**
   ```bash
   # Download from nodejs.org or use a package manager
   ```

2. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

3. **Run the app**
   ```bash
   # Start Metro bundler
   npm start
   
   # Or run on specific platform
   npm run ios      # iOS simulator (macOS only)
   npm run android  # Android emulator
   npm run web      # Web browser
   ```

## 🔧 Environment Setup

### Required API Keys

1. **OpenAI API Key** (for Pulse AI)
   - Sign up at [OpenAI](https://openai.com)
   - Get API key from dashboard
   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

2. **Supabase** (for database)
   - Create project at [Supabase](https://supabase.com)
   - Get URL and anon key from dashboard
   - Add to `.env`:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_anon_key
     ```

3. **Generate Secret Key**
   ```bash
   # Generate a secure secret key
   openssl rand -hex 32
   # Add to .env: SECRET_KEY=generated_key
   ```

### Database Setup (Supabase) - ✅ COMPLETED

**Schema Successfully Deployed:**

✅ **Database Status**: All beta optimization tables successfully created and deployed
✅ **Tables**: Core app tables + user_tiers, ai_usage_logs, user_feedback, usage_quotas  
✅ **Views**: daily_usage_stats, user_tier_stats, feedback_summary
✅ **Functions**: get_user_tier, log_ai_usage

The database schema has been fully deployed and is ready for production use. All admin endpoints and beta optimization features are now supported.

📖 **See `DEPLOYMENT_INSTRUCTIONS.md` for reference and troubleshooting.**

## 📱 MVP Features (Current)

### ✅ Completed
- [x] FastAPI backend with journal endpoints
- [x] Pulse AI service with OpenAI integration  
- [x] React Native app with navigation
- [x] Home dashboard with wellness stats
- [x] Journal entry screen with mood/energy/stress tracking
- [x] Pulse response screen with AI insights
- [x] TypeScript types and API service
- [x] **Supabase database integration** - ✅ Schema deployed
- [x] **Beta optimization features** - ✅ Admin endpoints, user tiers, usage tracking
- [x] **Production deployment** - ✅ Railway backend live

### 🎯 Ready for Next Phase
- [ ] User authentication flow
- [ ] Data persistence and sync  
- [ ] AI insight quality improvements
- [ ] Frontend integration testing
- [ ] User onboarding flow
- [ ] Mobile app deployment (iOS/Android)

### 📋 Next Sprint
- [ ] Journal history screen
- [ ] Detailed analytics/insights screen
- [ ] User profile and settings
- [ ] Push notifications for daily check-ins
- [ ] Streak tracking and gamification

## 🧠 Pulse AI Personality

Pulse is designed to be:
- **Gentle & Supportive**: Never clinical, always caring
- **Tech-Savvy**: Understands developer/designer challenges
- **Pattern-Aware**: Recognizes wellness trends over time
- **Actionable**: Provides specific, doable suggestions
- **Reflective**: Asks thoughtful follow-up questions

## 🔒 Privacy & Security

- All wellness data encrypted in transit and at rest
- No data sharing with third parties
- User controls their data completely
- Local storage for sensitive information
- GDPR/CCPA compliant design

## 📊 Success Metrics

- **60% next-day retention** - Users return for daily check-ins
- **70% helpful AI ratings** - Pulse insights are genuinely useful
- **3+ weekly interactions** - Sustainable engagement patterns
- **Reduced burnout indicators** - Measurable wellness improvements

## 🤝 Contributing

This is currently a personal project, but feedback and suggestions are welcome!

## 📄 License

See LICENSE file for details.

---

**Built with ❤️ for the tech community**

*Helping developers, designers, and tech workers maintain their wellness and prevent burnout through AI-powered insights and gentle daily check-ins.* 