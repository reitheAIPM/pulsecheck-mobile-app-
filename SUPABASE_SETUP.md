# PulseCheck - Supabase Database Setup Guide

## 🗄️ Database Setup Instructions

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose organization and enter project details:
   - **Name**: PulseCheck
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users
4. Wait for project to be created (~2 minutes)

### 2. Get Connection Details
After project creation, go to **Settings > API**:
- **Project URL**: Copy this (starts with https://xxx.supabase.co)
- **Project API Keys**:
  - **anon public**: Copy this (starts with eyJ...)
  - **service_role**: Copy this (starts with eyJ...) - Keep this secret!

### 3. Database Schema Setup

Go to **SQL Editor** in Supabase dashboard and run these SQL commands:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    tech_role VARCHAR(100),
    experience_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal entries table
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    work_challenges TEXT[],
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI insights table
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    insight_text TEXT NOT NULL,
    suggested_action TEXT,
    follow_up_question TEXT,
    insight_type VARCHAR(50),
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entries_created_at ON journal_entries(created_at);
CREATE INDEX idx_ai_insights_journal_entry_id ON ai_insights(journal_entry_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON journal_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 4. Row Level Security (RLS) Setup

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

-- Users can only see/edit their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Journal entries policies
CREATE POLICY "Users can view own journal entries" ON journal_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own journal entries" ON journal_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own journal entries" ON journal_entries
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own journal entries" ON journal_entries
    FOR DELETE USING (auth.uid() = user_id);

-- AI insights policies
CREATE POLICY "Users can view insights for own journal entries" ON ai_insights
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM journal_entries 
            WHERE journal_entries.id = ai_insights.journal_entry_id 
            AND journal_entries.user_id = auth.uid()
        )
    );

CREATE POLICY "Service can insert AI insights" ON ai_insights
    FOR INSERT WITH CHECK (true);
```

### 5. Authentication Setup

Go to **Authentication > Settings**:
1. **Site URL**: Add your app URLs:
   - `http://localhost:19006` (Expo development)
   - Your production domain when ready
2. **Email Templates**: Customize if desired
3. **Providers**: Enable email/password (default is fine for now)

### 6. Environment Variables

Create `.env` file in backend directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006

# Environment
ENVIRONMENT=development
```

### 7. Test Database Connection

After setting up environment variables:

```bash
cd backend
venv\Scripts\activate
python main.py
```

Should start without errors and show:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 8. API Testing

Test endpoints at: http://localhost:8000/docs

Key endpoints to test:
- `GET /health` - Should return {"status": "healthy"}
- `POST /journal/entries` - Create a journal entry
- `GET /journal/entries` - List journal entries
- `POST /journal/entries/{id}/pulse-response` - Generate AI insight

## 🔑 Security Notes

- **Never commit service_role key** to version control
- **Use anon key** for client-side operations
- **Use service_role key** only for server-side operations
- **Enable RLS** on all tables (done above)
- **Test RLS policies** before going to production

## 🚀 Production Checklist

- [ ] Database schema created
- [ ] RLS policies tested
- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] Authentication flow tested
- [ ] Data privacy compliance verified 