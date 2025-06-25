# PulseCheck - Development Environment Setup Guide

**Purpose**: Create separate development environment for safe testing while production remains stable  
**Priority**: ⚠️ **FUTURE TASK** - Only after core user experience issues are resolved  
**Current Focus**: Fixing critical UX issues for superb tester experience  
**Estimated Time**: 1-2 hours implementation (when ready)

---

## 🎯 **CURRENT PRIORITY: USER EXPERIENCE FIXES**

### **⚠️ BEFORE SETTING UP DEV ENVIRONMENT**
We must first fix critical user experience issues that are preventing testers from having a superb experience:

1. **🔴 AI End-to-End Functionality (CRITICAL)**
   - AI responses not generating after journal entries
   - Core value proposition broken - no AI insights

2. **🔴 Sign-In/Sign-Out Flow (CRITICAL)**
   - Authentication flow may have remaining issues
   - Users can't access the app or switch accounts

3. **🔴 Settings Persistence (HIGH)**
   - AI interaction preferences not saving (reverting to default)
   - Users lose their preferences, poor UX

4. **🔴 Journal Entry Creation (MEDIUM)**
   - May have remaining backend connectivity issues
   - Core journaling functionality potentially broken

5. **🔴 Error Handling & User Feedback (MEDIUM)**
   - Users see technical errors instead of helpful messages
   - Confusing experience, users don't know what's wrong

### **🎯 SUCCESS CRITERIA BEFORE DEV ENVIRONMENT**
- ✅ **Authentication**: Sign up, sign in, sign out all work flawlessly
- ✅ **Journal Entries**: Create, save, view entries without errors
- ✅ **AI Responses**: Every journal entry gets meaningful AI insight within 30 seconds
- ✅ **Settings**: User preferences save and persist correctly
- ✅ **Error Handling**: Users see helpful messages, not technical errors

---

## 🏗️ **FUTURE ARCHITECTURE OVERVIEW**

### **Current State (Problem)**
```
main branch → Vercel Production → Railway Production
     ↓              ↓                    ↓
All changes → Live Users → Production DB
```
**Issue**: Every change affects live users immediately

### **Target State (Solution)**
```
main branch → Vercel Production → Railway Production (Stable)
     ↓              ↓                    ↓
Live Users → Stable Experience → Prod Database

development branch → Vercel Preview → Railway Development
     ↓                    ↓                  ↓
Developers → Safe Testing → Dev Database

feature branches → Vercel Previews → Railway Development
     ↓                    ↓                  ↓
Review & Testing → Isolated Testing → Dev Database
```

---

## 📋 **IMPLEMENTATION CHECKLIST (FUTURE)**

### **Phase 1: Railway Development Backend**

#### **Step 1: Create Railway Development Service**
```bash
# Using Railway CLI (if available)
railway login
railway create pulsecheck-mobile-app-dev

# Alternative: Create through Railway dashboard
# 1. Go to railway.app
# 2. Click "New Project"
# 3. Name: "pulsecheck-mobile-app-dev"
# 4. Connect to same GitHub repo
# 5. Set branch filter to "development"
```

#### **Step 2: Configure Development Environment Variables**
```bash
# Development-specific Railway environment variables
JWT_SECRET=dev_dr3catCepCME4G1wQNzavTdoRMacRvtmtNcEU0P2t3GLzNvLpEVOxbBM0VkuzEs9yZWd4WbvzdoTj6BD0sPi2A==
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_API_KEY=[DEV_API_KEY_OR_SAME_AS_PROD]
ENVIRONMENT=development
```

#### **Step 3: Database Strategy**
**Option A: Separate Supabase Project (Recommended)**
```bash
# Create new Supabase project for development
# 1. Go to supabase.com
# 2. Create new project: "pulsecheck-dev"
# 3. Run migrations on dev database
# 4. Update SUPABASE_URL for dev environment
```

**Option B: Same Database with Schema Separation**
```sql
-- Create development schema in existing database
CREATE SCHEMA IF NOT EXISTS development;
-- Duplicate tables in development schema
-- Update RLS policies for schema separation
```

### **Phase 2: Vercel Development Configuration**

#### **Step 4: Create Development Branch**
```bash
git checkout main
git pull origin main
git checkout -b development
git push -u origin development
```

#### **Step 5: Configure Vercel Preview Deployments**
```json
// Update vercel.json for environment-specific builds
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://pulsecheck-mobile-app-dev.up.railway.app/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "https://pulsecheck-mobile-app-dev.up.railway.app",
    "VITE_ENVIRONMENT": "development"
  }
}
```

#### **Step 6: Environment-Specific Configuration**
```typescript
// Create src/config/environment.ts
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
  
  // Development-specific settings
  isDevelopment: import.meta.env.VITE_ENVIRONMENT === 'development',
  isProduction: import.meta.env.VITE_ENVIRONMENT === 'production',
  
  // Debug settings
  enableDebugLogs: import.meta.env.VITE_ENVIRONMENT !== 'production',
  enableMockServices: false // Always false after our fixes!
};
```

### **Phase 3: Branch Strategy & Workflow**

#### **Step 7: Git Branch Protection Rules**
```bash
# Protect main branch (production)
# 1. Go to GitHub repo settings
# 2. Branches → Add rule for "main"
# 3. Require pull request reviews
# 4. Require status checks to pass
# 5. Restrict pushes to main branch

# Set up development branch as integration branch
# 1. All feature branches merge to development first
# 2. Development testing happens on dev environment
# 3. Only stable development merges to main (production)
```

#### **Step 8: Deployment Workflow**
```bash
# Development workflow
feature/new-feature → development → Vercel Preview + Railway Dev
                                             ↓
                                    Testing & Validation
                                             ↓
development → main → Vercel Production + Railway Production
```

### **Phase 4: Environment Switching**

#### **Step 9: Update API Service for Environment Detection**
```typescript
// Update spark-realm/src/services/api.ts
import { config } from '../config/environment';

class ApiService {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: config.apiUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Environment': config.environment
      }
    });
    
    // Development-specific logging
    if (config.isDevelopment) {
      console.log('🔧 API Service Debug Info:');
      console.log('- Environment:', config.environment);
      console.log('- API URL:', config.apiUrl);
      console.log('- Debug Logs:', config.enableDebugLogs);
    }
  }
}
```

---

## 🧪 **TESTING & VALIDATION (FUTURE)**

### **Validation Checklist**
- [ ] **Development Backend**: Dev Railway service responds at `/health`
- [ ] **Development Frontend**: Vercel preview deployment loads correctly
- [ ] **Environment Isolation**: Dev changes don't affect production
- [ ] **Database Separation**: Dev and prod data are isolated
- [ ] **Authentication**: Auth works in both environments
- [ ] **API Integration**: Frontend connects to correct backend per environment
- [ ] **Environment Variables**: Proper configuration per environment

### **Test Scenarios**
1. **Development Testing**:
   ```bash
   # Push to development branch
   git checkout development
   git commit -m "Test development environment"
   git push origin development
   
   # Verify: Preview deployment uses dev backend
   # Verify: Changes don't affect production users
   ```

2. **Production Deployment**:
   ```bash
   # Merge to main (via PR)
   git checkout main
   git merge development
   git push origin main
   
   # Verify: Production deployment uses prod backend
   # Verify: Users see stable, tested features
   ```

---

## 🎯 **SUCCESS CRITERIA (FUTURE)**

### **Development Environment Setup Complete When**:
- ✅ **Separate Railway Services**: Dev and prod backends isolated
- ✅ **Branch-based Deployments**: Automatic preview deployments working
- ✅ **Environment Configuration**: Proper variable separation
- ✅ **Database Isolation**: Dev testing doesn't affect prod data
- ✅ **Testing Workflow**: Safe space for feature development
- ✅ **Production Stability**: Users have consistent experience

### **Benefits Achieved**:
- 🔒 **Production Stability**: No more disruptions for testing
- ⚡ **Faster Development**: Safe iteration space
- 🧪 **Proper Testing**: Full validation before production
- 👥 **Team Collaboration**: Multiple developers can work safely
- 📊 **Better Monitoring**: Separate metrics for dev vs prod

---

## 🚀 **NEXT STEPS**

### **Immediate (Current Priority)**:
1. Fix AI response generation end-to-end
2. Validate complete authentication flow
3. Fix settings persistence issues
4. Complete end-to-end user journey testing
5. Achieve superb tester experience

### **Future (After Core Functionality)**:
1. Create Railway development service
2. Set up development branch and Vercel previews
3. Configure environment variables
4. Test development workflow

**Target**: Complete core UX fixes first, then implement development environment for future stability! 