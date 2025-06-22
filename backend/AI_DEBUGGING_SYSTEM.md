# AI Debugging System for PulseCheck

## 🎯 **Overview**

This document provides a comprehensive debugging system designed specifically for AI assistants (like Claude) to quickly identify, diagnose, and fix deployment issues in the PulseCheck backend without human intervention.

## 🚀 **Quick Start for AI Debugging**

### **1. Run the AI-Optimized Build Pipeline**
```bash
cd backend
python build.py
```

This single command runs the entire validation and debugging pipeline:
- ✅ Import validation (application code only)
- 🔧 Auto-fix critical issues
- ✅ Pre-deployment validation
- 🏥 Health check tests
- 📋 Comprehensive reporting

### **2. Check Build Status**
- **Success**: Exit code 0 → Ready for Railway deployment
- **Failure**: Exit code 1 → Check `build_report.json` for detailed analysis

## 📊 **AI Debugging Tools**

### **Core Validation Scripts**

#### **1. `validate_imports.py` - Import Validation**
- **Purpose**: Validates application imports (ignores third-party packages)
- **Focus**: Only checks `app/` directory and main.py
- **Output**: `import_validation_report.json`
- **AI Context**: Provides specific fix recommendations for missing modules/attributes

```bash
python validate_imports.py
```

#### **2. `pre_deploy_check.py` - Pre-Deployment Validation**
- **Purpose**: Comprehensive startup validation
- **Checks**: Critical imports, environment variables, database models, API endpoints, service dependencies
- **Output**: `pre_deployment_report.json`
- **AI Context**: Categorizes issues as critical (blocks deployment) vs warnings

```bash
python pre_deploy_check.py
```

#### **3. `build.py` - Complete Build Pipeline**
- **Purpose**: Orchestrates all validation and provides final deployment readiness
- **Features**: Timing, error handling, AI recommendations
- **Output**: `build_report.json`

## 🔧 **Common Issues & AI Fixes**

### **Issue Type 1: Missing Service Files**
**Symptoms**: `ModuleNotFoundError: No module named 'app.services.journal_service'`

**AI Fix Pattern**:
```python
# Create missing service file
from app.core.config import settings
from supabase import create_client, Client

class JournalService:
    def __init__(self):
        self.supabase = create_client(settings.supabase_url, settings.supabase_service_key)
    
    # Add required methods based on router imports
```

### **Issue Type 2: Missing Attributes in Modules**
**Symptoms**: `AttributeError: module 'app.services.journal_service' has no attribute 'JournalService'`

**AI Fix Pattern**:
1. Check what's being imported in router files
2. Add missing class/function to the module
3. Ensure proper export in `__init__.py` if needed

### **Issue Type 3: Configuration Issues**
**Symptoms**: `AttributeError: 'Settings' object has no attribute 'SUPABASE_URL'`

**AI Fix Pattern**:
1. Check `app/core/config.py` for field names (lowercase vs uppercase)
2. Update service files to use correct field names
3. Ensure environment variables match config fields

### **Issue Type 4: SQLAlchemy Base Missing**
**Symptoms**: `cannot import name 'Base' from 'app.core.database'`

**AI Fix Pattern**:
```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
```

## 📋 **AI Report Analysis**

### **build_report.json Structure**
```json
{
  "build_status": "success|failed",
  "pipeline_steps": [...],
  "deployment_ready": true|false,
  "ai_recommendations": [
    "🎉 BUILD SUCCESSFUL - All pipeline steps completed",
    "🚀 Ready for Railway deployment"
  ]
}
```

### **AI Decision Tree**
1. **build_status = "success"** → Deploy to Railway
2. **build_status = "failed"** → Check failed steps:
   - Import issues → Create missing modules/classes
   - Config issues → Fix environment variables/settings
   - Health check issues → Fix application startup

## 🛠 **AI Debugging Workflow**

### **Step 1: Initial Assessment**
```bash
python build.py
```

### **Step 2: Issue Classification**
- **Critical**: Blocks deployment (import errors, syntax errors)
- **Warning**: Reduces functionality (missing env vars)

### **Step 3: Automated Fixes**
The system provides specific fix recommendations:
- Missing modules → Create with template
- Missing attributes → Add to existing module
- Config mismatches → Update field names

### **Step 4: Validation**
Re-run build pipeline to confirm fixes

## 🚨 **Railway Deployment Issues**

### **Common Railway Errors & Fixes**

#### **1. Build Configuration**
```toml
# railway.toml
[build]
builder = "NIXPACKS"
watchPatterns = ["backend/**"]
```

#### **2. Health Check Failures**
- Check OPTIONS request handling
- Ensure all imports work without environment variables
- Test main.py can be imported

#### **3. Server Startup Issues**
- Missing service instances
- Import errors on startup
- Environment variable issues

## 📚 **AI Knowledge Base**

### **File Structure Understanding**
```
backend/
├── app/
│   ├── core/          # Configuration, database
│   ├── models/        # Data models (Pydantic)
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── main.py           # FastAPI app
└── requirements.txt  # Dependencies
```

### **Critical Dependencies**
- **FastAPI**: Web framework
- **Supabase**: Database client
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM (optional)
- **OpenAI**: AI services

### **Environment Variables (Railway)**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

## 🔄 **Continuous Improvement**

### **AI Learning Points**
1. **Proactive vs Reactive**: Use validation before deployment
2. **Systematic Approach**: Follow the build pipeline
3. **Context Awareness**: Understand the bigger picture
4. **Documentation**: Update this file with new patterns

### **Success Metrics**
- ✅ Build pipeline passes (exit code 0)
- ✅ All critical validations pass
- ✅ Railway deployment succeeds
- ✅ Health checks pass

## 💡 **AI Best Practices**

1. **Always run the build pipeline first** before making changes
2. **Focus on critical issues** before warnings
3. **Use the provided templates** for creating missing files
4. **Validate fixes** by re-running the pipeline
5. **Check Railway logs** for deployment-specific issues

## 🎯 **Success Criteria**

The AI debugging system is successful when:
- AI can identify issues in < 30 seconds
- AI can fix issues without human intervention
- Deployment success rate > 95%
- Zero recurring issues

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: AI Debugging System 