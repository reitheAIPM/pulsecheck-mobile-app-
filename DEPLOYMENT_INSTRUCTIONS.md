# 🚀 PulseCheck Deployment Instructions

## Project Cleanup Complete ✅

I've cleaned up the messy project structure and created a single, comprehensive schema file based on official Supabase documentation.

## 📁 What Was Cleaned Up

**Removed duplicate/problematic files:**
- `supabase_compatible_schema.sql` ❌
- `compatible_schema.sql` ❌
- `supabase_fixed_schema.sql` ❌
- `fixed_schema.sql` ❌
- `minimal_working_schema.sql` ❌
- `backend/beta_optimization_schema.sql` ❌
- `backend/supabase_schema_idempotent.sql` ❌

**Single source of truth:**
- `DEPLOY_TO_SUPABASE.sql` ✅ (This is the ONLY file you need)

## 🎯 Deployment Steps

### Step 1: Deploy Database Schema

1. Go to your Supabase SQL Editor: https://supabase.com/dashboard/project/qwpwlubxhtuzvmvajjjr/sql
2. Copy the entire contents of `DEPLOY_TO_SUPABASE.sql`
3. Paste into the SQL Editor
4. Click "Run" 
5. You should see success messages like:
   ```
   🚀 PULSECHECK DEPLOYMENT COMPLETE!
   ✅ Tables: 7 out of 7
   ✅ Views: 3 out of 3
   ✅ Functions: 2 out of 2
   🎉 SUCCESS: All features deployed!
   ```

### Step 2: Verify Deployment

If you encounter any errors during deployment, use the diagnostic tool:

1. **Run Diagnostics**: Copy contents of `DIAGNOSE_SCHEMA.sql` and run in Supabase SQL Editor
2. **Check Results**: Look for missing tables, columns, or specific error messages
3. **Fix Issues**: The diagnostic will tell you exactly what's missing

**Quick verification queries:**
```sql
-- Check critical columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'ai_usage_logs' 
AND column_name = 'created_at';

-- Test analytics views
SELECT * FROM daily_usage_stats LIMIT 5;
SELECT * FROM user_tier_stats;
```

### Step 3: Restart Railway

1. Go to your Railway dashboard
2. Redeploy your backend to pick up the new schema
3. Your app should now have all beta optimization features

## 🔧 What This Schema Provides

### ✅ Core Features
- **User Management**: Complete user system with tiers
- **Journal Entries**: Mood, energy, stress tracking
- **AI Integration**: Usage logging and cost tracking
- **Analytics**: Real-time usage statistics
- **Security**: Row Level Security (RLS) enabled

### ✅ Beta Optimization Features
- **User Tiers**: Free, Premium, Beta user levels
- **Rate Limiting**: Usage quotas per user tier
- **Cost Tracking**: AI usage and cost monitoring
- **Feedback System**: User feedback collection
- **Admin Analytics**: Dashboard views for monitoring

### ✅ Performance
- **Optimized Indexes**: Fast queries on common patterns
- **Efficient Views**: Pre-computed analytics
- **Helper Functions**: Easy tier management and logging

## 🔍 Key Improvements Made

1. **Single Schema File**: No more confusion with multiple versions
2. **Supabase Native**: Uses `uuid_generate_v4()` and proper `public.` schema
3. **Backward Compatible**: Works with existing data
4. **No Complex Functions**: Removed problematic date casting
5. **Production Ready**: Proper RLS, indexes, and constraints

## 📊 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Test health check
curl https://pulsecheck-mobile-app-production.up.railway.app/

# Test admin analytics (should now work)
curl https://pulsecheck-mobile-app-production.up.railway.app/admin/analytics

# Test user tiers
curl https://pulsecheck-mobile-app-production.up.railway.app/admin/user-tiers
```

## 🎉 Success Criteria

Your deployment is successful when:
- [ ] Schema deploys without errors
- [ ] All 7 tables are created
- [ ] All 3 views work
- [ ] Admin endpoints return data (not 404)
- [ ] AI responses include proper insights
- [ ] Rate limiting works by user tier

## 🆘 Troubleshooting Common Issues

### ❌ "Column 'created_at' does not exist"
**Cause**: Views trying to reference columns before tables are created
**Solution**: 
1. Run `DIAGNOSE_SCHEMA.sql` to see what's missing
2. The improved `DEPLOY_TO_SUPABASE.sql` now has proper execution order
3. If still failing, tables may not be created due to foreign key issues

### ❌ "Column 'endpoint' does not exist"  
**Cause**: `ai_usage_logs` table not created properly
**Solution**:
```sql
-- Check if table exists
SELECT * FROM information_schema.tables WHERE table_name = 'ai_usage_logs';

-- Check if column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'ai_usage_logs' AND column_name = 'endpoint';
```

### ❌ Foreign Key Constraint Errors
**Cause**: Referencing `auth.users` but table doesn't exist
**Solution**: The schema creates `public.users` instead - this is normal

### ❌ Permission Denied Errors
**Cause**: RLS policies preventing access
**Solution**: Check if you're running as database owner in Supabase

### 🔧 General Debugging Steps:
1. **Run Diagnostics**: Use `DIAGNOSE_SCHEMA.sql` first
2. **Check Supabase Logs**: Project dashboard → Logs  
3. **Verify Execution Order**: Tables → Indexes → Views → Functions
4. **Check Dependencies**: Ensure referenced tables exist first

## 📈 Next Steps After Deployment

1. **Monitor Usage**: Check `daily_usage_stats` view
2. **Set User Tiers**: Promote beta users manually
3. **Test AI Features**: Verify enhanced responses
4. **Monitor Costs**: Track AI usage and costs
5. **Collect Feedback**: Enable user feedback collection

---

**This is now a clean, production-ready deployment.** No more messy schema files! 🎯 