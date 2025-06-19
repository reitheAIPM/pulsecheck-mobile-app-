# Database Setup Log - PulseCheck Project

## 🎯 **Objective**
Execute the complete database schema in Supabase to enable end-to-end testing of the PulseCheck application.

---

## 📋 **Pre-Setup Status**

### **Environment Configuration** ✅
- **Supabase URL**: `https://qwpwlubxhtuzvmvajjjr.supabase.co`
- **API Keys**: ✅ Configured in backend `.env` file
- **Backend Connection**: ✅ Tested and working
- **Schema File**: `backend/supabase_schema.sql` ready

### **Required Tables**
1. `users` - User authentication and profile data
2. `checkins` - User mood and wellness check-ins
3. `ai_analyses` - AI-generated insights from check-ins

---

## 🔄 **Setup Process**

### **Step 1: Access Supabase Dashboard** ✅
- **Time**: June 18, 2024, 2:30 PM EST
- **Action**: Navigate to Supabase project dashboard
- **URL**: https://supabase.com/dashboard/project/qwpwlubxhtuzvmvajjjr
- **Status**: ✅ Completed

### **Step 2: Open SQL Editor** ✅
- **Time**: June 18, 2024, 2:31 PM EST
- **Action**: Navigate to SQL Editor in Supabase dashboard
- **Location**: Dashboard → SQL Editor
- **Status**: ✅ Completed

### **Step 3: Verify Connection** ✅
- **Time**: June 18, 2024, 2:40 PM EST
- **Action**: Test Supabase connection with credentials
- **Result**: ✅ Connection successful (expected "users table does not exist" error)
- **Status**: ✅ Completed

### **Step 4: Execute Schema Script** 🔄
- **Time**: June 18, 2024, 2:41 PM EST
- **Action**: Copy and paste the complete schema from `backend/supabase_schema.sql`
- **Expected Duration**: 2-3 minutes
- **Status**: 🔄 Ready to Execute

**Schema Content to Execute**:
```sql
-- PulseCheck Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CheckIns table
CREATE TABLE IF NOT EXISTS checkins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_score INTEGER CHECK (energy_score >= 1 AND energy_score <= 10),
    stress_score INTEGER CHECK (stress_score >= 1 AND stress_score <= 10),
    journal_entry TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Analyses table
CREATE TABLE IF NOT EXISTS ai_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    checkin_id UUID REFERENCES checkins(id) ON DELETE CASCADE,
    insight TEXT NOT NULL,
    suggested_action TEXT,
    follow_up_question TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_checkins_user_timestamp ON checkins(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_checkins_user_created ON checkins(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_user_created ON ai_analyses(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analyses ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);

-- Create RLS policies for checkins table
CREATE POLICY "Users can view own checkins" ON checkins
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own checkins" ON checkins
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own checkins" ON checkins
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own checkins" ON checkins
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Create RLS policies for ai_analyses table
CREATE POLICY "Users can view own ai analyses" ON ai_analyses
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own ai analyses" ON ai_analyses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own ai analyses" ON ai_analyses
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own ai analyses" ON ai_analyses
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Grant necessary permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON checkins TO authenticated;
GRANT ALL ON ai_analyses TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Show created tables
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename IN ('users', 'checkins', 'ai_analyses')
ORDER BY tablename;
```

### **Step 5: Verify Table Creation** ⏳
- **Time**: [To be filled]
- **Action**: Check that all tables were created successfully
- **Tables to Verify**:
  - [ ] `users`
  - [ ] `checkins`
  - [ ] `ai_analyses`
- **Status**: ⏳ Pending

### **Step 6: Verify Indexes** ⏳
- **Time**: [To be filled]
- **Action**: Confirm all indexes were created
- **Indexes to Verify**:
  - [ ] `idx_checkins_user_timestamp`
  - [ ] `idx_checkins_user_created`
  - [ ] `idx_ai_analyses_user_created`
  - [ ] `idx_users_email`
- **Status**: ⏳ Pending

### **Step 7: Verify Row Level Security** ⏳
- **Time**: [To be filled]
- **Action**: Confirm RLS policies are active
- **Policies to Verify**:
  - [ ] Users can only access their own data
  - [ ] Checkins are user-scoped
  - [ ] AI analyses are user-scoped
- **Status**: ⏳ Pending

---

## 📊 **Schema Details**

### **Table: users**
```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Table: checkins**
```sql
CREATE TABLE checkins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_score INTEGER CHECK (energy_score >= 1 AND energy_score <= 10),
    stress_score INTEGER CHECK (stress_score >= 1 AND stress_score <= 10),
    journal_entry TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Table: ai_analyses**
```sql
CREATE TABLE ai_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    checkin_id UUID REFERENCES checkins(id) ON DELETE CASCADE,
    insight TEXT NOT NULL,
    suggested_action TEXT,
    follow_up_question TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🚨 **Potential Issues & Solutions**

### **Issue 1: Permission Errors**
- **Symptoms**: "Permission denied" errors during table creation
- **Cause**: Insufficient database privileges
- **Solution**: Use service role key or contact Supabase support

### **Issue 2: Constraint Violations**
- **Symptoms**: Foreign key or check constraint errors
- **Cause**: Invalid data or constraint definitions
- **Solution**: Review constraint definitions and test data

### **Issue 3: Index Creation Failures**
- **Symptoms**: Index creation errors
- **Cause**: Duplicate indexes or naming conflicts
- **Solution**: Drop existing indexes first, then recreate

---

## ✅ **Success Criteria**

### **Database Setup Complete When**:
- [ ] All 3 tables created successfully
- [ ] All 4 indexes created successfully
- [ ] Row Level Security policies active
- [ ] No SQL errors in execution log
- [ ] Backend can connect and perform basic operations

### **Testing Verification**:
- [ ] User registration works
- [ ] Checkin creation works
- [ ] AI analysis generation works
- [ ] Data retrieval works
- [ ] Error handling works correctly

---

## 📝 **Execution Notes**

### **Pre-Execution Checklist**:
- [x] Supabase dashboard accessible
- [x] SQL schema file ready
- [x] Backend environment configured
- [x] Connection verified and working
- [x] Test data prepared

### **Post-Execution Checklist**:
- [ ] All tables verified
- [ ] All indexes verified
- [ ] RLS policies verified
- [ ] Backend connection tested
- [ ] Basic CRUD operations tested

---

**Created**: June 18, 2024
**Last Updated**: June 18, 2024, 2:41 PM EST
**Status**: 🔄 Ready to Execute Schema 