# Comprehensive Monitoring System - Test Guide 🧪

*Date: January 30, 2025*

## 🎯 **Testing Your Bulletproof Monitoring System**

This guide will help you verify that all the comprehensive monitoring capabilities are working correctly and ready for production use.

---

## 🚀 **Quick System Test**

### **Step 1: Quick Health Check**

First, let's verify the monitoring system is accessible:

```bash
# Test quick health check endpoint
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/comprehensive-monitoring/quick-health-check" \
  -H "Accept: application/json"
```

**Expected Response** (healthy system):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T10:00:00Z",
  "components": {
    "database": "healthy",
    "scheduler": "healthy",
    "ai_services": "healthy"
  },
  "alerts": [],
  "quick_check": true
}
```

### **Step 2: Configuration Validation Test**

Test the configuration validation system:

```bash
# Test comprehensive configuration validation
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/config-validation/comprehensive" \
  -H "Accept: application/json"
```

**Expected Response** (valid configuration):
```json
{
  "overall_status": "valid",
  "validation_duration_seconds": 2.1,
  "individual_results": {
    "cors": {"status": "valid"},
    "database_schema": {"status": "valid"},
    "environment": {"status": "valid"}
  },
  "consolidated_recommendations": [],
  "critical_issues": []
}
```

### **Step 3: Predictive Analytics Test**

Test the predictive monitoring capabilities:

```bash
# Test risk assessment
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/predictive-monitoring/risk-assessment" \
  -H "Accept: application/json"
```

**Expected Response** (low risk system):
```json
{
  "overall_risk": "low",
  "risk_indicators": {
    "error_trend_risk": "low",
    "performance_risk": "low",
    "anomaly_risk": "low"
  },
  "immediate_actions_needed": false,
  "timestamp": "2025-01-30T10:00:00Z"
}
```

### **Step 4: Auto-Resolution Test**

Test auto-resolution capabilities (dry run):

```bash
# Test CORS issue resolution (dry run)
curl -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auto-resolution/test-resolution/cors_issues?dry_run=true" \
  -H "Accept: application/json"
```

**Expected Response**:
```json
{
  "test_mode": true,
  "issue_type": "cors_issues",
  "procedure_available": true,
  "estimated_actions": [
    "Would analyze issue",
    "Would apply resolution steps",
    "Would validate resolution",
    "Would report results"
  ],
  "message": "Test successful - procedure is available and ready"
}
```

---

## 🧪 **Comprehensive Test Suite**

### **Test 1: Full System Analysis**

Run a complete system analysis to test all monitoring components:

```bash
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/comprehensive-monitoring/complete-analysis" \
  -H "Accept: application/json"
```

**What This Tests**:
- Configuration validation
- Predictive analytics
- System health monitoring
- Issue detection
- Resolution recommendations

### **Test 2: Individual Configuration Tests**

Test each configuration validation component separately:

```bash
# Test CORS configuration
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/config-validation/cors"

# Test database schema  
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/config-validation/database-schema"

# Test environment configuration
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/config-validation/environment"
```

### **Test 3: Predictive Monitoring Components**

Test individual predictive monitoring features:

```bash  
# Test error trend analysis
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/predictive-monitoring/error-trends?hours_back=24"

# Test performance trends
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/predictive-monitoring/performance-trends?hours_back=24"

# Test capacity prediction
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/predictive-monitoring/capacity-prediction"

# Test anomaly detection
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/predictive-monitoring/anomaly-detection?hours_back=12"
```

### **Test 4: Auto-Resolution Procedures**

Test all available auto-resolution procedures:

```bash
# List available procedures
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auto-resolution/available-procedures"

# Test each procedure (dry run)
curl -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auto-resolution/test-resolution/database_connection_issues?dry_run=true"
curl -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auto-resolution/test-resolution/performance_degradation?dry_run=true"
curl -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auto-resolution/test-resolution/high_error_rate?dry_run=true"
```

---

## ✅ **Success Criteria**

### **All Tests Should Pass With:**

1. **Health Check**: Status = "healthy", no alerts
2. **Configuration Validation**: overall_status = "valid", no critical issues
3. **Risk Assessment**: overall_risk = "low", no immediate actions needed
4. **Auto-Resolution**: All procedures available and ready
5. **Complete Analysis**: overall_system_status = "healthy"

### **Performance Benchmarks:**

- **Quick Health Check**: < 2 seconds response time
- **Configuration Validation**: < 5 seconds response time  
- **Complete Analysis**: < 10 seconds response time
- **All Endpoints**: Return valid JSON responses

---

## 🚨 **Troubleshooting**

### **If Health Check Fails:**
```bash
# Check basic connectivity
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/health"

# Check debug endpoint
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/health"
```

### **If Configuration Validation Fails:**
- Check individual validation endpoints
- Review error messages in response
- Verify environment variables are set
- Check database connectivity

### **If Predictive Analytics Fail:**
- Verify monitoring data is available
- Check if enough historical data exists
- Review time range parameters

### **If Auto-Resolution Tests Fail:**
- Verify procedures are registered
- Check procedure availability endpoint
- Review error messages in responses

---

## 🎯 **Production Readiness Checklist**

After running all tests, verify:

- [ ] ✅ Quick health check returns "healthy"
- [ ] ✅ Configuration validation passes all checks
- [ ] ✅ Predictive analytics show "low" risk
- [ ] ✅ All auto-resolution procedures are available
- [ ] ✅ Complete analysis shows "healthy" system status
- [ ] ✅ All API responses are under performance benchmarks
- [ ] ✅ No critical issues detected in any test
- [ ] ✅ Resolution history is tracking properly

**When all tests pass**: Your comprehensive monitoring system is ready for production! 🎉 