# 🧪 PulseCheck Testing Suite

Comprehensive testing infrastructure for the PulseCheck mobile app project.

## 🚀 Quick Start

### **Unified Testing (Recommended)**
```powershell
# Run both AI and comprehensive tests (default)
./unified_testing.ps1

# Quick AI analysis only (30 seconds)
./unified_testing.ps1 quick

# Full system validation only (2-3 minutes)  
./unified_testing.ps1 full
```

## 📁 Available Test Scripts

### **🎯 `unified_testing.ps1` - All-in-One Solution**
- **Combines both AI and comprehensive testing**
- **3 modes**: `quick`, `full`, or `both` (default)
- **Unified results** with separate AI vs System metrics
- **Smart analysis** with color-coded health assessment

### **🤖 `ai_automated_testing.ps1` - AI Analysis Only**
- Tests AI system's self-analysis capabilities
- 5 AI debug endpoints
- Quick insights into system health
- AI-powered failure prediction

### **🔍 `comprehensive_testing.ps1` - Full System Validation**
- Tests all critical system components
- 30+ endpoints across 9 categories
- Authentication, database, user flows
- Edge case and error handling

## 🎛️ Testing Modes Explained

### **Quick Mode** (`quick`)
**Use when**: Daily health checks, quick status validation
**Tests**: AI analysis endpoints only (5 tests)
**Time**: ~30 seconds
**Focus**: AI insights, risk assessment, performance grading

### **Full Mode** (`full`) 
**Use when**: Pre-deployment, investigating issues, comprehensive validation
**Tests**: All system components (30+ tests)
**Time**: 2-3 minutes
**Focus**: Authentication, database, user flows, edge cases

### **Both Mode** (default)
**Use when**: Complete system validation, troubleshooting, regular checks
**Tests**: AI analysis + comprehensive testing (35+ tests)
**Time**: 3-4 minutes
**Focus**: Complete system health assessment

## 📊 Test Categories

### **🤖 AI Analysis**
- AI System Health
- Failure Point Prediction
- Risk Assessment
- Performance Grading
- System Summary

### **📡 Infrastructure**
- Backend Health
- API Status
- Root Endpoint

### **🔐 Authentication**
- JWT Validation
- Auth Failures
- Token Security
- Login Endpoints

### **📔 Journal System**
- Entry Creation
- Stats Generation
- User Data Access
- Authentication Requirements

### **🗄️ Database**
- Connection Health
- Performance Metrics
- RLS Configuration
- Query Validation

### **🎯 Adaptive AI**
- User Preferences
- AI Learning System
- Personalization

### **⚡ Edge Cases**
- Malformed Requests
- Invalid Endpoints
- Error Handling
- Security Boundaries

### **👑 Admin Systems**
- Admin Authentication
- Beta Metrics
- System Controls

### **📊 Monitoring**
- Debug Systems
- Live Streams
- Error Tracking
- Performance Monitoring

## 📈 Understanding Results

### **Success Rate Interpretation**
- **90%+**: 🎉 Excellent - Production ready
- **80-89%**: ✅ Good - Minor issues
- **60-79%**: ⚠️ Concerning - Investigation needed
- **<60%**: 🚨 Critical - Immediate attention required

### **Result Categories**
- **Expected Failures**: Security tests that should block unauthorized access
- **Unexpected Failures**: Actual system issues requiring attention
- **Success**: Working endpoints and functionality

## 🔧 Troubleshooting

### **Common Issues**

**Timeouts**: Check Railway deployment status
```powershell
# Quick health check
curl.exe "https://pulsecheck-mobile-app-production.up.railway.app/health"
```

**Authentication Failures**: Expected for security endpoints
- These are often "good failures" showing security is working

**Database Errors**: Check Supabase connection
- Monitor RLS policies and connection pools

**PowerShell Execution Policy**:
```powershell
# If script won't run
powershell -ExecutionPolicy Bypass -File ./unified_testing.ps1
```

## 📋 Integration with AI Documentation

This testing suite is referenced in:
- `ai/AI-DEBUGGING-SYSTEM.md` - Debug capabilities
- `ai/CURRENT-STATUS.md` - System health monitoring
- `ai/LAUNCH-READINESS-ASSESSMENT.md` - Pre-launch validation

## 🎯 Best Practices

### **Daily Workflow**
```powershell
# Morning system check
./unified_testing.ps1 quick

# Pre-deployment validation
./unified_testing.ps1 full

# Post-deployment verification
./unified_testing.ps1
```

### **CI/CD Integration**
```yaml
# Example GitHub Action
- name: Run PulseCheck Tests
  run: |
    cd tests
    powershell -ExecutionPolicy Bypass -File ./unified_testing.ps1 full
```

### **Issue Investigation**
1. Start with `quick` mode for AI insights
2. Run `full` mode for comprehensive validation
3. Check specific failed endpoints manually
4. Review AI analysis recommendations

## 📞 Support

For testing issues:
1. Check Railway deployment status
2. Verify Supabase connectivity
3. Review failed test details in output
4. Check AI recommendations in quick mode

---

**Last Updated**: $(Get-Date)  
**Maintainer**: PulseCheck Development Team 