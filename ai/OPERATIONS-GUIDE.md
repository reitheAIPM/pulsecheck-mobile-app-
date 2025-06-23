# Operations Guide - PulseCheck Project

**Purpose**: Consolidated deployment, debugging, and production operations for AI assistance  
**Last Updated**: January 27, 2025  
**Status**: 🚨 **CRITICAL OPERATIONS CRISIS** - Journal system down

---

## 🚨 **CURRENT PRODUCTION CRISIS**

### **Crisis Status: Journal Router Complete Failure**
**Discovered**: January 27, 2025  
**Impact**: 100% of journal functionality unavailable  
**Status**: 🚨 **ACTIVE CRISIS** - Immediate operations response required

#### **Crisis Assessment**
- **Service Health**: ✅ Backend operational (health endpoint working)
- **Journal System**: ❌ All endpoints returning 404 (complete router failure)
- **User Impact**: ❌ Cannot create, read, or manage journal entries
- **AI Features**: ❌ Topic classification and AI responses unavailable

#### **Emergency Operations Response**
```bash
# 1. IMMEDIATE DIAGNOSTICS
curl https://pulsecheck-mobile-app-production.up.railway.app/health  # ✅ Expected: 200 OK
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/test  # ❌ Returns: 404

# 2. RAILWAY DEPLOYMENT CHECK
railway logs --tail 100  # Check for startup errors

# 3. SERVICE DEPENDENCY TEST
# Test if authentication service is causing router mount failures
```

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **Railway Deployment Architecture**
- **Platform**: Railway (automated deployments)
- **Production URL**: `https://pulsecheck-mobile-app-production.up.railway.app`
- **Deployment Method**: Git push triggers automatic build and deploy
- **Health Check**: `GET /health` endpoint for Railway service monitoring

### **Deployment Process**
```bash
# 1. Commit and push changes
git add .
git commit -m "Fix: description of changes"
git push origin main

# 2. Monitor deployment
railway logs --tail 50

# 3. Verify deployment health
curl https://pulsecheck-mobile-app-production.up.railway.app/health

# 4. Test critical endpoints
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/test
```

### **Environment Variables Configuration**
```bash
# Railway Production Environment
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
SUPABASE_ANON_KEY=[configured in Railway dashboard]
SUPABASE_SERVICE_KEY=[configured in Railway dashboard]
OPENAI_API_KEY=[intentionally not set - disabled for MVP]
PORT=8000
RAILWAY_STATIC_URL=https://pulsecheck-mobile-app-production.up.railway.app
```

### **Deployment Success Metrics**
- **Build Success**: Code compilation and dependency installation
- **Health Check**: `/health` endpoint returns 200 OK within 60 seconds
- **Router Availability**: All API endpoints respond appropriately
- **Service Dependencies**: Database and external services accessible

---

## 🔍 **AI-OPTIMIZED DEBUGGING SYSTEM**

### **System Overview**
PulseCheck features a comprehensive AI-optimized debugging system designed for rapid issue resolution and production monitoring.

### **Debug Endpoints (Currently Unknown Status)**
```bash
# AI Self-Testing Endpoint
POST /api/v1/journal/ai/self-test
# Comprehensive AI system validation with automated testing

# AI Debug Summary Endpoint  
GET /api/v1/journal/ai/debug-summary
# Complete debugging context for AI analysis

# Topic Classification Testing
POST /api/v1/journal/ai/topic-classification
# Real-time content analysis validation
```

### **Error Classification System**
The monitoring system categorizes errors into 8 categories for AI pattern recognition:
1. **UNKNOWN**: Unclassified errors
2. **API_ENDPOINT**: Endpoint accessibility issues
3. **DATABASE**: Connection and query problems
4. **AUTHENTICATION**: User authentication failures
5. **VALIDATION**: Input validation errors
6. **OPENAI_API**: AI service integration issues
7. **NETWORK**: Connectivity problems
8. **SYSTEM**: Infrastructure and environment issues

### **AI Debug Context Structure**
Every error includes comprehensive AI debugging context:
```python
@dataclass
class DebugContext:
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: str
    severity: ErrorSeverity
    category: ErrorCategory
    
    # AI Debugging Context
    function_name: str
    line_number: int
    file_path: str
    module_name: str
    
    # System Context
    system_info: Dict[str, Any]
    environment_vars: Dict[str, str]
    request_context: Optional[Dict[str, Any]]
    user_context: Optional[Dict[str, Any]]
    
    # AI Problem-Solving Context
    similar_errors: List[str]
    potential_causes: List[str]
    suggested_solutions: List[str]
    debugging_steps: List[str]
```

---

## 📊 **MONITORING & ANALYTICS**

### **Performance Baselines**
```python
# AI Operation Performance Targets
performance_baselines = {
    "topic_classification_ms": 50.0,      # Topic classification time
    "persona_selection_ms": 100.0,        # Persona selection time
    "pattern_analysis_ms": 200.0,         # User pattern analysis time
    "ai_response_generation_ms": 2000.0,  # AI response generation time
    "total_response_time_ms": 2500.0      # Total adaptive response time
}
```

### **System Health Metrics**
- **API Response Time (P95)**: Target <500ms, Current ~280ms ✅
- **Database Query Time (Avg)**: Target <100ms, Current ~50ms ✅
- **Error Rate**: Target <1%, Current **100% for journal endpoints** ❌
- **System Uptime**: Target >99%, Current affected by crisis
- **AI Response Generation**: Target <3s, Current unavailable ❌

### **Error Rate Monitoring**
```python
def calculate_error_rate():
    total_errors = sum(error_patterns.values())
    total_operations = len(debug_contexts)
    error_rate = total_errors / max(total_operations, 1)
    
    if error_rate > 0.1:  # 10% error rate threshold
        logger.error(f"High error rate detected: {error_rate:.1%}")
        return False
    return True
```

---

## 🚨 **CRISIS RECOVERY PROCEDURES**

### **Crisis Classification**
1. **CRITICAL**: Core functionality completely broken (Current Status)
2. **HIGH**: Major features unavailable but system partially functional
3. **MEDIUM**: Performance degradation or minor feature issues
4. **LOW**: Cosmetic issues or non-critical feature problems

### **Current Crisis: Router Mount Failure**
**Classification**: CRITICAL
**Impact**: All journal functionality unavailable
**Recovery Strategy**: Systematic debugging and emergency fallback deployment

#### **Emergency Recovery Steps**
```bash
# 1. IMMEDIATE ASSESSMENT
curl https://pulsecheck-mobile-app-production.up.railway.app/health
# ✅ Expected: {"status": "healthy"} - Confirms service is running

# 2. ROUTER AVAILABILITY TEST
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/test
# ❌ Current: 404 Not Found - Confirms router mounting issue

# 3. RAILWAY LOGS ANALYSIS
railway logs --tail 100
# Look for: import errors, dependency failures, authentication issues

# 4. DEPENDENCY CHAIN TEST
# Test if authentication dependencies are causing cascade failures
```

### **Emergency Fallback Deployment**
```python
# Create minimal journal router without complex dependencies
@router.get("/test")
async def emergency_test():
    """Emergency endpoint to verify router mounting"""
    return {"status": "emergency_mode", "router": "mounted"}

@router.post("/entries")
async def emergency_create_entry(content: str):
    """Emergency journal creation without authentication"""
    return {"status": "emergency_saved", "content": content}
```

### **Recovery Validation Checklist**
```bash
# ✅ Service Health
curl /health  # Returns 200 OK

# ✅ Router Mount
curl /api/v1/journal/test  # Returns 200 OK

# ✅ Core Functionality
curl -X POST /api/v1/journal/entries -d '{"content":"test"}'  # Returns 201 Created

# ✅ Authentication Flow
curl -H "Authorization: Bearer test_token" /api/v1/journal/entries  # Returns 200 OK

# ✅ AI Features
curl -X POST /api/v1/journal/ai/topic-classification -d '{"content":"test"}'  # Returns 200 OK
```

---

## 🛡️ **CRISIS PREVENTION SYSTEM**

### **Enhanced Pre-Deployment Checklist**
Based on previous Railway deployment crisis resolution:

```bash
# Infrastructure Validation (MANDATORY)
✅ Import testing: python -m py_compile app/routers/*.py
✅ Database pattern check: Consistent get_database usage
✅ Router health validation: Individual endpoint testing
✅ Fallback verification: Empty routers ready for failures
✅ Environment variables: All required vars present
✅ Health endpoint: /health returns 200 OK

# CRITICAL: Router Mount Testing (ENHANCED)
✅ Journal router test: /api/v1/journal/test returns 200 OK
✅ Core endpoint test: /api/v1/journal/entries returns 200 OK (GET)
✅ Authentication flow: All protected endpoints properly authenticated
✅ Service dependencies: All required services available during startup
✅ Circular dependency check: No import cycles in router dependencies
```

### **Automated CI/CD Pipeline**
```yaml
# Future implementation
name: Pre-deployment Validation
on:
  push:
    branches: [main]
  
jobs:
  validate:
    steps:
      - name: Import Testing
        run: python -m py_compile app/routers/*.py
      
      - name: Router Health Check
        run: python test_router_availability.py
      
      - name: Service Dependency Test
        run: python test_service_dependencies.py
      
      - name: Emergency Fallback Test
        run: python test_emergency_fallbacks.py
```

### **Success Pattern Recognition**
Based on successful Railway deployment crisis resolution (January 27, 2025):

1. **Systematic Debugging**: Health → Routers → Dependencies → Environment
2. **Import Validation**: Test all router imports before deployment
3. **Fallback Patterns**: Empty routers prevent total system failure
4. **Database Consistency**: Single pattern usage (`get_database` vs `get_db`)
5. **Health Check Enhancement**: Validate schema AND endpoints, not just service

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Database Query Optimization**
```python
# Optimized query patterns
async def get_user_journal_entries_optimized(user_id: str, limit: int = 10):
    """Optimized journal retrieval with minimal database calls"""
    query = """
        SELECT id, content, mood_level, energy_level, stress_level, created_at
        FROM journal_entries 
        WHERE user_id = $1 
        ORDER BY created_at DESC 
        LIMIT $2
    """
    return await database.fetch_all(query, user_id, limit)
```

### **AI Response Caching**
```python
# Cache frequently requested AI responses
@lru_cache(maxsize=100)
def get_cached_persona_response(content_hash: str, persona: str):
    """Cache AI responses for identical content and persona combinations"""
    return cached_responses.get(f"{content_hash}:{persona}")
```

### **Error Recovery Optimization**
```python
# Exponential backoff for external service failures
async def call_external_service_with_retry(service_call, max_retries=3):
    """Optimized retry logic for external service calls"""
    for attempt in range(max_retries):
        try:
            return await service_call()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## 🔧 **MAINTENANCE PROCEDURES**

### **Daily Operations Checklist**
```bash
# 1. System Health Validation
curl https://pulsecheck-mobile-app-production.up.railway.app/health

# 2. Critical Endpoint Testing
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/test

# 3. Error Rate Monitoring
railway logs --tail 50 | grep -i error

# 4. Performance Metrics Review
# Check response times and throughput metrics

# 5. User Feedback Monitoring
# Review any user-reported issues or feedback
```

### **Weekly Maintenance Tasks**
1. **Database Performance Review**: Query optimization and index analysis
2. **Error Pattern Analysis**: Review recurring issues and solutions
3. **Security Audit**: Check for vulnerabilities and update dependencies
4. **Backup Verification**: Ensure data backup and recovery procedures work
5. **Capacity Planning**: Monitor resource usage and scaling needs

### **Emergency Contact Procedures**
1. **Critical Issues**: Immediate response required within 1 hour
2. **Service Outages**: Communications to users via status page
3. **Data Incidents**: Privacy team notification and user communication
4. **Security Breaches**: Immediate containment and investigation

---

**This file consolidates: deployment-guide.md, ai-debugging-guide.md, debugging-capabilities-summary.md, production-deployment-status.md** 