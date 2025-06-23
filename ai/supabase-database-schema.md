# Supabase Database Schema Reference

## Overview
This document outlines the current Supabase database schema for PulseCheck, including all tables, relationships, and authentication setup.

## Authentication Setup
- **Provider**: Supabase Auth (built-in)
- **Current Status**: Using browser session authentication with `X-User-Id` headers
- **Database**: `qwpwlubxhtuzvmvajjjr.supabase.co`

## Core Tables

### 1. **profiles** (User Management)
**Purpose**: Main user profile table connected to Supabase Auth
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  tech_role TEXT,
  company TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  -- Privacy & Preferences
  data_sharing_consent BOOLEAN DEFAULT FALSE,
  analytics_consent BOOLEAN DEFAULT FALSE,
  -- Account Management
  role TEXT DEFAULT 'user',
  provider TEXT DEFAULT 'email',
  last_login TIMESTAMPTZ
);
```

### 2. **journal_entries** (Core Functionality)
**Purpose**: User journal entries with mood tracking
```sql
CREATE TABLE journal_entries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  mood_level INTEGER CHECK (mood_level >= 1 AND mood_level <= 10),
  energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
  stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
  sleep_hours NUMERIC,
  work_hours NUMERIC,
  tags TEXT[],
  work_challenges TEXT[],
  gratitude_items TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  ai_insights JSONB,
  ai_generated_at TIMESTAMPTZ
);
```

### 3. **ai_insights** (AI Analysis Results)
**Purpose**: Store AI-generated insights and responses
```sql
CREATE TABLE ai_insights (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
  insight_type TEXT NOT NULL, -- 'pulse_response', 'pattern_analysis', 'weekly_summary'
  content JSONB NOT NULL,
  confidence_score NUMERIC CHECK (confidence_score >= 0 AND confidence_score <= 1),
  persona_used TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB
);
```

### 4. **user_patterns** (Pattern Analysis)
**Purpose**: Store analyzed user patterns for personalization
```sql
CREATE TABLE user_patterns (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE UNIQUE,
  writing_style TEXT,
  common_topics TEXT[],
  mood_trends JSONB,
  interaction_preferences JSONB,
  response_preferences JSONB,
  pattern_confidence NUMERIC,
  entries_analyzed INTEGER DEFAULT 0,
  last_analyzed TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5. **weekly_summaries** (Analytics)
**Purpose**: Store weekly wellness summaries
```sql
CREATE TABLE weekly_summaries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  week_start DATE NOT NULL,
  week_end DATE NOT NULL,
  summary_type TEXT DEFAULT 'automated',
  content JSONB NOT NULL,
  metrics JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. **feedback** (Quality Improvement)
**Purpose**: Store user feedback on AI responses
```sql
CREATE TABLE feedback (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
  ai_insight_id UUID REFERENCES ai_insights(id) ON DELETE CASCADE,
  feedback_type TEXT NOT NULL, -- 'thumbs_up', 'thumbs_down', 'report', 'detailed'
  feedback_text TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB
);
```

## Row Level Security (RLS) Policies

### Current Security Model
All tables use RLS to ensure users can only access their own data:

```sql
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Example policy for journal_entries
CREATE POLICY "Users can view own journal entries" ON journal_entries
  FOR ALL USING (user_id = auth.uid());
```

## Authentication Flow Recommendations

### Phase 1: Enhanced Browser Session (Current + Improved)
**Keep existing system but make it more robust:**

1. **User Registration Flow**:
   ```javascript
   // Frontend: Register with Supabase Auth
   const { data, error } = await supabase.auth.signUp({
     email: 'user@example.com',
     password: 'password123',
     options: {
       data: {
         name: 'John Doe',
         tech_role: 'Software Engineer',
         company: 'Tech Corp'
       }
     }
   })
   ```

2. **Automatic Profile Creation**:
   ```sql
   -- Database trigger to create profile on auth.users insert
   CREATE OR REPLACE FUNCTION create_profile_for_user()
   RETURNS TRIGGER AS $$
   BEGIN
     INSERT INTO profiles (id, email, name, tech_role, company)
     VALUES (
       NEW.id,
       NEW.email,
       NEW.raw_user_meta_data->>'name',
       NEW.raw_user_meta_data->>'tech_role',
       NEW.raw_user_meta_data->>'company'
     );
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER create_profile_trigger
     AFTER INSERT ON auth.users
     FOR EACH ROW EXECUTE FUNCTION create_profile_for_user();
   ```

3. **Session Management**:
   ```javascript
   // Use Supabase session instead of custom headers
   const { data: { session } } = await supabase.auth.getSession()
   const userId = session?.user?.id
   ```

### Phase 2: OAuth Integration (Future)
Add social login while maintaining Supabase Auth:
- Google OAuth
- GitHub OAuth  
- Microsoft OAuth

## Current Issues & Solutions

### ❌ **Issue 1: Journal Entries Not Appearing**
**Root Cause**: User ID mismatch between session and database queries
**Solution**: Use Supabase Auth consistently instead of custom headers

### ❌ **Issue 2: Data Isolation Problems**
**Root Cause**: Hardcoded user IDs and inconsistent authentication
**Solution**: Implement proper Supabase Auth with RLS policies

### ❌ **Issue 3: Complex Custom Authentication**
**Root Cause**: Reinventing authentication instead of using Supabase features
**Solution**: Leverage Supabase Auth built-in features

## Implementation Plan

### Immediate (Phase 1)
1. **Replace custom headers with Supabase Auth**
2. **Add profile creation trigger**
3. **Update all API calls to use Supabase session**
4. **Test with real user registration/login**

### Short-term (Phase 2)
1. **Add OAuth providers to Supabase project**
2. **Implement social login UI**
3. **Add profile completion flow**

### Long-term (Phase 3)
1. **Advanced user management**
2. **Team/organization features**
3. **Enterprise authentication**

## Database Connection Details
- **URL**: `https://qwpwlubxhtuzvmvajjjr.supabase.co`
- **Environment**: Production
- **Authentication**: Supabase Auth with RLS
- **Tables**: 6 core tables with proper relationships
- **Security**: Row Level Security enabled on all tables

## Migration Strategy
1. **Keep existing data intact**
2. **Add Supabase Auth registration/login**
3. **Migrate existing sessions to proper auth**
4. **Gradually phase out custom authentication**
5. **Add OAuth when stable**

This schema supports the full PulseCheck feature set while maintaining data security and user privacy through Supabase's built-in authentication and RLS system. 