# Railway Environment Variable Setup Guide

## 🚨 CRITICAL: Database Timeout Issue Resolution

**ISSUE**: Database endpoints hanging due to missing `SUPABASE_SERVICE_ROLE_KEY`  
**STATUS**: Environment variable added to local .env but missing from Railway  
**SOLUTION**: Add SUPABASE_SERVICE_ROLE_KEY to Railway Dashboard

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### 1. Access Railway Dashboard
- Go to: https://railway.app/
- Login to your account
- Select the **PulseCheck** project

### 2. Navigate to Environment Variables
- Click on your **PulseCheck service/project**
- Go to the **"Variables"** tab (or **"Environment"** section)

### 3. Add Missing Environment Variable
Click **"Add Variable"** and enter:

**Variable Name**: `SUPABASE_SERVICE_ROLE_KEY`  
**Variable Value**: [Your Supabase Service Role Key from .env file]

> **⚠️ Security Note**: The service role key should start with `eyJ...` and be much longer than the anon key

### 4. Save and Deploy
- Click **"Save"** or **"Add"**  
- Railway will automatically redeploy (takes 2-3 minutes)
- Monitor the deployment logs for success

---

## 🔍 VERIFICATION STEPS

After adding the environment variable, test these endpoints:

### 1. Check Environment Status
```powershell
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/environment"
```
**Expected**: `SUPABASE_SERVICE_ROLE_KEY: "✅ Set"`

### 2. Comprehensive Database Test
```powershell
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"
```
**Expected**: `overall_status: "✅ HEALTHY"`

### 3. Test Auth Signup (Critical Test)
```powershell
curl.exe -X POST -H "Content-Type: application/json" -d "{\"email\":\"test@test.com\",\"password\":\"test123\"}" "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/signup"
```
**Expected**: Response in under 5 seconds with user creation success

### 4. Test Journal Operations
```powershell
# After getting auth token from signup, test journal entry creation
curl.exe -X POST -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d "{\"content\":\"Test entry\",\"mood_level\":7}" "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/entries"
```

---

## 🎯 EXPECTED RESULTS

### ✅ BEFORE FIX:
- ✅ Health endpoint: 126ms (working)
- ✅ CORS test: Working  
- ✅ Auth health: Working
- ❌ Auth signup: Hangs after 10+ seconds
- ❌ Journal operations: Timeout
- ❌ Database queries: Fail

### ✅ AFTER FIX:
- ✅ Health endpoint: Still fast
- ✅ Auth signup: Complete in 2-5 seconds
- ✅ Journal operations: Working
- ✅ Database queries: Success
- ✅ All endpoints: Operational

---

## 🚨 TROUBLESHOOTING

### If the fix doesn't work immediately:

1. **Wait 5 minutes** for Railway deployment to complete
2. **Check deployment logs** in Railway dashboard
3. **Verify the key is correct** (starts with `eyJ`, very long string)
4. **Test the monitoring endpoint**:
   ```powershell
   curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/wait-for-fix"
   ```

### Common Issues:
- **Deployment still in progress**: Wait for Railway build to complete
- **Wrong key format**: Ensure you copied the service role key, not anon key
- **Typo in variable name**: Must be exactly `SUPABASE_SERVICE_ROLE_KEY`

---

## 📊 MONITORING ENDPOINTS

Use these endpoints to monitor the fix:

- **Real-time status**: `/api/v1/database/comprehensive-status`
- **Environment check**: `/api/v1/database/environment`  
- **Fix monitoring**: `/api/v1/database/wait-for-fix`
- **Simple test**: `/api/v1/database/simple-ping`

---

## 🎉 SUCCESS CONFIRMATION

**The fix is successful when:**
1. All database endpoints respond in under 5 seconds
2. Auth signup creates users successfully  
3. Journal entries can be created and retrieved
4. Comprehensive status shows "✅ HEALTHY"
5. Environment variables all show "✅ Set"

**Expected timeline**: 2-5 minutes after adding the environment variable. 