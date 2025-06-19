# Railway Deployment Guide

## 🚀 Quick Deployment Steps

Your backend is **ready for Railway deployment**! Follow these steps:

### 1. Railway Account Setup

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect GitHub** account to Railway
3. **Create new project** from your GitHub repository

### 2. Project Configuration

1. **Select Repository**: Choose your `PulseCheck` repository
2. **Select Service**: Railway will detect your Python app automatically
3. **Configure Build**: Railway will use the `requirements.txt` and `Procfile`

### 3. Environment Variables

In your Railway dashboard, add these environment variables:

```env
ENVIRONMENT=production
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_generated_secret_key_here
PORT=8000
HOST=0.0.0.0
```

### 4. Generate Secret Key

Generate a secure secret key for production:

```bash
# Windows PowerShell
[System.Web.Security.Membership]::GeneratePassword(32, 0)

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Deploy

1. **Push to GitHub**: Commit and push your changes
2. **Railway Auto-Deploy**: Railway will automatically build and deploy
3. **Monitor Logs**: Check the deployment logs in Railway dashboard
4. **Test Endpoints**: Visit your Railway URL + `/health`

## 📋 Deployment Checklist

### Pre-Deployment
- [x] Backend runs locally (`python backend/main.py`)
- [x] All dependencies in `requirements.txt`
- [x] Environment variables configured
- [x] Railway configuration files created
- [ ] Supabase database schema executed
- [ ] API keys obtained (Supabase, OpenAI)

### During Deployment
- [ ] Railway project created
- [ ] GitHub repository connected
- [ ] Environment variables set
- [ ] Build completed successfully
- [ ] Service started without errors

### Post-Deployment
- [ ] Health check endpoint responds (`/health`)
- [ ] API documentation accessible (`/docs`)
- [ ] Database connections working
- [ ] AI endpoints responding
- [ ] CORS configured for frontend

## 🧪 Testing Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "PulseCheck API",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. API Documentation
Visit: `https://your-app.railway.app/docs`

### 3. Test Endpoints
```bash
# Test root endpoint
curl https://your-app.railway.app/

# Test API endpoints
curl https://your-app.railway.app/api/v1/checkins/
```

## 🔧 Configuration Files

### `railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd backend && python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### `Procfile`
```
web: cd backend && python main.py
```

### `requirements.txt`
All dependencies including:
- FastAPI and Uvicorn
- Supabase client
- OpenAI API
- Authentication libraries
- Email validator

## 🚨 Common Issues & Solutions

### Build Failures
- **Issue**: Missing dependencies
- **Solution**: Check `requirements.txt` includes all packages

### Startup Errors
- **Issue**: Environment variables not set
- **Solution**: Verify all required env vars in Railway dashboard

### Database Connection Issues
- **Issue**: Supabase connection fails
- **Solution**: Check SUPABASE_URL and SUPABASE_KEY are correct

### CORS Issues
- **Issue**: Frontend can't connect to API
- **Solution**: Update CORS origins in `config.py`

## 📊 Monitoring

### Railway Dashboard
- **Metrics**: CPU, memory, network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### Application Monitoring
- **Health Checks**: Automatic health monitoring
- **Error Tracking**: Monitor application errors
- **Performance**: API response times

## 🔄 Continuous Deployment

### Automatic Deployments
- **GitHub Integration**: Auto-deploy on push to main branch
- **Environment Branches**: Different environments for different branches
- **Rollback**: Easy rollback to previous deployments

### Manual Deployments
- **Railway CLI**: Deploy from command line
- **Dashboard**: Manual deployment trigger
- **Branch Selection**: Deploy specific branches

## 📝 Post-Deployment Tasks

### 1. Update Frontend API URL
```typescript
// frontend/src/services/api.ts
private baseURL = 'https://your-app.railway.app/api/v1';
```

### 2. Test End-to-End Flow
- Create journal entry from mobile app
- Verify data saves to Supabase
- Test AI response generation

### 3. Monitor Performance
- Check API response times
- Monitor error rates
- Verify database queries

## 🎯 Success Criteria

✅ **Deployment Successful When**:
- Health endpoint returns 200 OK
- API documentation loads
- Database connections work
- Frontend can communicate with backend
- AI endpoints generate responses
- No critical errors in logs

---

## 🚀 Ready to Deploy!

Your backend is **production-ready** with:
- ✅ FastAPI application structure
- ✅ Environment configuration
- ✅ Database integration
- ✅ AI service integration
- ✅ CORS configuration
- ✅ Health check endpoints
- ✅ Comprehensive error handling

**Next Step**: Create your Railway project and deploy! 🎉 