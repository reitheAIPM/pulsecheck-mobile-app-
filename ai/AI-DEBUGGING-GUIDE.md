# AI Debugging Guide 🔍
*Critical Debugging Information for PulseCheck AI System*  
*Last Updated: January 31, 2025*

## 🚨 **CRITICAL: Service Role Client for AI Operations**

### **The Database Client Problem**
**Most Critical AI Issue**: AI services using wrong database client type

#### **Two Client Types in Supabase**

1. **Anon Client** (`get_client()`)
   - Uses `SUPABASE_ANON_KEY`
   - Subject to RLS policies
   - Requires JWT authentication
   - **Use for**: User-facing operations

2. **Service Role Client** (`get_service_client()`)
   - Uses `SUPABASE_SERVICE_ROLE_KEY`
   - **Bypasses ALL RLS policies**
   - Full database access
   - **Use for**: AI/Backend operations

#### **Critical Rule for AI Services**
```python
# 🚨 ALWAYS use service role client for AI operations
client = self.db.get_service_client()

# ❌ WRONG - Will fail due to RLS restrictions
client = self.db.get_client()
```

### **Symptoms of Wrong Client Usage**
- AI reports "0 journal entries found" when entries exist
- Scheduler shows "no_active_users"
- Database queries successful but return empty results
- AI system appears healthy but generates no responses

---

## 🔍 **Production Debug Endpoints**

### **Database Client Validation**
```bash
# Check which client type AI is using
GET /api/v1/debug/database/client-validation

# Test service role access
GET /api/v1/debug/database/service-role-test

# RLS policy analysis
GET /api/v1/debug/database/rls-analysis
```

### **AI System Diagnostics**
```bash
# Comprehensive AI health check
GET /api/v1/comprehensive-monitoring/quick-health-check

# AI diagnostic for specific user
GET /api/v1/debug/ai-diagnostic/{user_id}

# Scheduler status and processing
GET /api/v1/scheduler/status
GET /api/v1/scheduler/analytics
```

### **Manual Testing**
```bash
# Trigger manual AI cycle
POST /api/v1/scheduler/manual-cycle?cycle_type=main

# Test AI response generation
POST /api/v1/journal/entries/{entry_id}/adaptive-response
```

---

## ⚠️ **Common Issues & Solutions**

### **Issue 1: AI Not Responding**
**Symptoms**:
- Journal entries created successfully
- AI scheduler running without errors
- No AI responses generated

**Diagnosis**:
```bash
# Check database client type
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/client-validation

# Expected result for working system:
{
  "ai_service_client": "service_role",
  "entries_accessible": 15,
  "note": "Should access all entries (bypasses RLS)"
}
```

**Solution**:
```python
# Fix in AI services
client = self.db.get_service_client()  # Not get_client()
```

### **Issue 2: Content Safety Filter Blocking**
**Symptoms**:
- AI generation appears to work
- Validation errors on response conversion
- Warning: "Content safety issue detected"

**Diagnosis**:
Look for overly aggressive content safety patterns:
```python
# BAD - Too aggressive
"medical_advice": [r"you're"]  # Blocks normal conversation

# GOOD - Specific patterns
"medical_advice": [r"you're (?:sick|ill|depressed)"]
```

**Solution**:
Update content safety patterns to be more specific and less aggressive.

### **Issue 3: Schema Mismatches**
**Symptoms**:
- Database connection working
- Column not found errors

**Common Mismatches**:
```python
# Wrong column names
.select('mood_rating')  # Should be 'mood_level'
.select('persona')      # Should be 'persona_used'
```

**Solution**:
Verify column names match database schema exactly.

---

## 🛡️ **Circuit Breaker Pattern**

### **AI Reliability Protection**
```python
class AICircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=300):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    async def call_with_fallback(self, ai_function, fallback_function):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                return await fallback_function()
        
        try:
            result = await ai_function()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self._record_failure(e)
            return await fallback_function()
```

### **Smart Fallback Responses**
```python
async def fallback_ai_response(entry_content: str, persona: str):
    """Intelligent fallback when AI services fail"""
    fallback_responses = {
        "pulse": "I hear you. Sometimes it helps to take a moment and breathe.",
        "sage": "This sounds like an important reflection. What insights does this bring?",
        "spark": "I can sense there's energy in what you're sharing. What's next?",
        "anchor": "Thank you for sharing this. You're taking positive steps."
    }
    return fallback_responses.get(persona, fallback_responses["pulse"])
```

---

## 📊 **Performance Monitoring**

### **Key Metrics to Track**
- **AI Response Time**: Target <3 seconds
- **Service Role Client Usage**: Should be 100% for AI operations
- **Circuit Breaker State**: Monitor OPEN states
- **Content Safety Blocks**: Track false positives
- **Database Query Performance**: Monitor RLS bypass effectiveness

### **Monitoring Commands**
```bash
# Performance metrics
GET /api/v1/debug/performance-metrics

# Error patterns
GET /api/v1/debug/error-patterns

# Service health
GET /api/v1/comprehensive-monitoring/complete-analysis
```

---

## 🔧 **Implementation Checklist**

### **When Adding New AI Features**

1. **Database Access**
   - [ ] Use `get_service_client()` for AI operations
   - [ ] Use `get_client()` only for user-facing operations
   - [ ] Add comment explaining client choice

2. **Error Handling**
   - [ ] Implement circuit breaker pattern
   - [ ] Create intelligent fallback responses
   - [ ] Add comprehensive logging

3. **Testing**
   - [ ] Test with manual cycle trigger
   - [ ] Verify service role client access
   - [ ] Check content safety patterns
   - [ ] Validate schema column names

4. **Monitoring**
   - [ ] Add performance metrics
   - [ ] Track error patterns
   - [ ] Monitor circuit breaker states

---

## 🚨 **Emergency Procedures**

### **AI System Down**
1. Check Railway deployment status
2. Verify environment variables (especially service role key)
3. Test database connectivity
4. Check OpenAI API status
5. Review recent code changes

### **Database Access Issues**
1. Verify service role client usage
2. Check RLS policies
3. Test with manual queries
4. Validate schema column names

### **Performance Degradation**
1. Check circuit breaker states
2. Monitor OpenAI API rate limits
3. Review database query performance
4. Check content safety filter efficiency

---

## 📋 **Quick Reference**

### **Essential Debug Commands**
```bash
# System health
curl https://pulsecheck-mobile-app-production.up.railway.app/health

# AI diagnostics
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/client-validation

# Manual AI trigger
curl -X POST https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/manual-cycle?cycle_type=main

# Scheduler status
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status
```

### **Critical Files to Monitor**
- `backend/app/core/database.py` - Database client functions
- `backend/app/services/comprehensive_proactive_ai_service.py` - Main AI service
- `backend/app/services/advanced_scheduler_service.py` - Background processing
- `backend/app/routers/journal.py` - AI endpoint implementations

---

**🎯 Bottom Line**: Most AI issues stem from database client type confusion. Always use service role client for AI operations and anon client for user operations. 