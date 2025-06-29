# Sentry Error Tracking Setup Guide

## Overview
Sentry provides real-time error tracking and performance monitoring for your PulseCheck application.

## Setup Steps

### 1. Create Sentry Account
1. Go to [sentry.io](https://sentry.io)
2. Sign up for a free account
3. Create a new project:
   - Platform: Python (for backend)
   - Project name: `pulsecheck-backend`

### 2. Get Your DSN
After creating the project, you'll receive a DSN (Data Source Name) that looks like:
```
https://abc123@o123456.ingest.sentry.io/1234567
```

### 3. Configure Environment Variables

Add to your `.env` file:
```bash
# Sentry Configuration
SENTRY_DSN=https://your-dsn-here@sentry.io/project-id
SENTRY_ENVIRONMENT=development  # or production, staging
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
```

### 4. Backend Integration

The Sentry SDK is already integrated in your backend. Here's how it works:

```python
# app/core/observability.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

def initialize():
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
```

## Features You Get

### 1. Automatic Error Capture
- All unhandled exceptions are automatically sent to Sentry
- Stack traces with source code context
- User context (if available)

### 2. Performance Monitoring
- API endpoint performance
- Database query performance
- External API call tracking (OpenAI)

### 3. Custom Error Context
Your app already adds context for AI operations:
```python
# Example from your code
sentry_sdk.set_context("ai_operation", {
    "user_id": user_id,
    "persona": persona,
    "model": "gpt-4",
    "tokens_used": token_count
})
```

### 4. Error Grouping
Sentry automatically groups similar errors together, making it easier to:
- Identify patterns
- Track error frequency
- See which errors affect most users

## Monitoring Dashboard

Once configured, you can:

1. **View Errors**: See all errors with full stack traces
2. **Performance**: Monitor slow endpoints and database queries
3. **Releases**: Track errors by deployment
4. **Alerts**: Set up notifications for error spikes

## Best Practices

### 1. Add User Context
```python
sentry_sdk.set_user({
    "id": user_id,
    "email": user_email,
    "subscription_tier": tier
})
```

### 2. Add Custom Tags
```python
sentry_sdk.set_tag("ai.persona", persona_name)
sentry_sdk.set_tag("feature", "journal_entry")
```

### 3. Capture Custom Events
```python
# For important non-error events
sentry_sdk.capture_message(
    "AI rate limit exceeded",
    level="warning",
    extras={"user_id": user_id, "requests_today": count}
)
```

## Environment-Specific Settings

### Development
```bash
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0  # 100% for testing
```

### Production
```bash
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% to reduce volume
```

## Debugging Tips

1. **Test Sentry Connection**:
   ```python
   # Add to a test endpoint
   sentry_sdk.capture_exception(Exception("Test error"))
   ```

2. **Check Configuration**:
   ```python
   print(f"Sentry configured: {sentry_sdk.Hub.current.client is not None}")
   ```

3. **View in Logs**:
   - Errors sent to Sentry will show in your logs
   - Look for "Sentry event sent" messages

## Cost Considerations

Free tier includes:
- 5,000 errors/month
- 10,000 performance events/month
- 1 user
- 30-day data retention

For a beta app, this is usually sufficient.

## Security Notes

- Never commit your DSN to version control
- Use environment variables for all Sentry settings
- DSN is safe to expose in frontend (different from API keys)
- Don't log sensitive user data in error messages 