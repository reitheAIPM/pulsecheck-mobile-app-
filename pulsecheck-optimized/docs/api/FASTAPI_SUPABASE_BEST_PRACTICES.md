# FastAPI + Supabase Best Practices Guide

## 🎯 Purpose
This guide prevents recurring issues found in our codebase, including:
- **11 duplicate datetime handling patterns** 
- **Supabase query syntax errors** (like the `head=True` issue)
- **Missing endpoint documentation**
- **Inconsistent error handling**

---

## 📅 DateTime Handling Best Practices

### ✅ DO: Use Centralized Utilities
```python
from app.core.utils import DateTimeUtils

# Instead of repeating this pattern 11 times:
if 'updated_at' not in entry or entry['updated_at'] is None:
    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))

# Use this:
entry = DateTimeUtils.ensure_updated_at(entry)
```

### ✅ DO: Handle Bulk Operations
```python
# For multiple entries:
entries = DateTimeUtils.ensure_updated_at_bulk(entries)
```

### ✅ DO: Normalize DateTime Fields
```python
# Ensure timezone-aware and consistent format
entry = DateTimeUtils.normalize_datetime_fields(entry)
```

### ❌ DON'T: Repeat DateTime Logic
```python
# BAD - Found in 11 places in our codebase
if 'updated_at' not in entry or entry['updated_at'] is None:
    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
```

---

## 🗄️ Supabase Query Best Practices

### ✅ DO: Use Safe Query Utilities
```python
from app.core.utils import SupabaseQueryUtils

# Safe count query
total = SupabaseQueryUtils.safe_count_query(
    client, 
    "journal_entries", 
    filters={"user_id": user_id}
)

# Safe range query
entries = SupabaseQueryUtils.safe_range_query(
    client,
    "journal_entries",
    offset=0,
    limit=30,
    filters={"user_id": user_id}
)
```

### ✅ DO: Validate Pagination
```python
# Prevent invalid pagination parameters
page, per_page = SupabaseQueryUtils.validate_pagination(page, per_page)
```

### ❌ DON'T: Use Unsupported Parameters
```python
# BAD - This caused our 500 error
count_result = client.table("journal_entries").select("*", count="exact", head=True)

# GOOD - head=True is not supported in Supabase Python client
count_result = client.table("journal_entries").select("id", count="exact")
```

### ✅ DO: Handle .in_() Queries Properly
```python
# Correct syntax for filtering by list of IDs
insights_result = client.table("ai_insights").select("*").in_("journal_entry_id", entry_ids)
```

---

## 🔧 Endpoint Development Best Practices

### ✅ DO: Follow Standard Pattern
```python
@router.get("/endpoint-name")
@limiter.limit("30/minute")
async def endpoint_function(
    request: Request,  # Required for rate limiter
    page: int = 1,
    per_page: int = 30,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Clear docstring explaining what this endpoint does.
    """
    try:
        # 1. Validate parameters
        page, per_page = SupabaseQueryUtils.validate_pagination(page, per_page)
        
        # 2. Get client (service role for reading AI insights)
        client = db.get_service_client()
        
        # 3. Execute queries with error handling
        total = SupabaseQueryUtils.safe_count_query(client, "table_name", {"user_id": current_user["id"]})
        
        # 4. Handle datetime fields
        entries = DateTimeUtils.ensure_updated_at_bulk(entries)
        
        # 5. Return consistent response format
        return ResponseUtils.format_pagination_response(entries, page, per_page, total)
        
    except Exception as e:
        logger.error(f"Error in endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### ✅ DO: Update Documentation Immediately
When creating new endpoints, **immediately** update:
- `backend/API_DOCUMENTATION.md`
- Include request/response examples
- Specify authentication requirements
- Document rate limits

---

## 📊 Response Formatting Best Practices

### ✅ DO: Use Consistent Pagination Format
```python
from app.core.utils import ResponseUtils

return ResponseUtils.format_pagination_response(
    data=entries,
    page=page,
    per_page=per_page,
    total=total
)
```

### ✅ DO: Use Consistent Error Format
```python
return ResponseUtils.format_error_response(
    error_message="Invalid request",
    error_code="VALIDATION_ERROR",
    details={"missing_fields": ["user_id"]}
)
```

---

## 🔐 Authentication & Security

### ✅ DO: Use Proper Client Based on Operation
```python
# For user-specific operations (respects RLS)
auth_header = request.headers.get('Authorization')
if auth_header and auth_header.startswith('Bearer '):
    jwt_token = auth_header.split(' ')[1]
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(jwt_token)

# For AI insights reading (bypasses RLS)
service_client = db.get_service_client()
```

### ✅ DO: Validate User Permissions
```python
from app.core.utils import ValidationUtils

# Validate UUID format
if not ValidationUtils.validate_uuid(entry_id):
    raise HTTPException(status_code=400, detail="Invalid entry ID format")

# Validate required fields
missing_fields = ValidationUtils.validate_required_fields(
    data, 
    ["content", "mood_level"]
)
if missing_fields:
    raise HTTPException(
        status_code=400, 
        detail=f"Missing required fields: {', '.join(missing_fields)}"
    )
```

---

## 🚀 Performance Best Practices

### ✅ DO: Batch Database Operations
```python
# Get all entry IDs first
entry_ids = [entry['id'] for entry in entries]

# Then batch fetch AI insights
insights_result = client.table("ai_insights").select("*").in_("journal_entry_id", entry_ids)
```

### ✅ DO: Use Appropriate Rate Limits
```python
# Journal creation (expensive): 5/minute
@limiter.limit("5/minute")

# AI requests (expensive): 10/minute
@limiter.limit("10/minute")

# Read operations: 60/minute
@limiter.limit("60/minute")

# Stats/analytics: 30/minute
@limiter.limit("30/minute")
```

---

## 📋 Common Patterns to Avoid

### ❌ Pattern: Duplicate DateTime Handling
**Found in 11 places** - Always use `DateTimeUtils.ensure_updated_at()`

### ❌ Pattern: Manual Pagination Logic
**Error-prone** - Always use `SupabaseQueryUtils.validate_pagination()`

### ❌ Pattern: Inconsistent Error Handling
**Confusing for frontend** - Always use `ResponseUtils.format_error_response()`

### ❌ Pattern: Missing Documentation
**Causes integration issues** - Always update `API_DOCUMENTATION.md`

---

## 🔄 Migration Guide

### Step 1: Replace DateTime Handling
```python
# Find and replace all instances of:
if 'updated_at' not in entry or entry['updated_at'] is None:
    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))

# With:
from app.core.utils import DateTimeUtils
entry = DateTimeUtils.ensure_updated_at(entry)
```

### Step 2: Update Imports
```python
# Add to your router files:
from app.core.utils import (
    DateTimeUtils, 
    SupabaseQueryUtils, 
    ValidationUtils, 
    ResponseUtils
)
```

### Step 3: Test Endpoints
```python
# Test the refactored endpoints:
pytest tests/test_journal_endpoints.py::test_datetime_handling
```

---

## 🛡️ Error Prevention Checklist

Before creating any new endpoint:

- [ ] **DateTime**: Use `DateTimeUtils.ensure_updated_at()` for any database records
- [ ] **Pagination**: Use `SupabaseQueryUtils.validate_pagination()` for paginated endpoints
- [ ] **Validation**: Use `ValidationUtils.validate_required_fields()` for input validation
- [ ] **Queries**: Use `SupabaseQueryUtils.safe_count_query()` and `safe_range_query()`
- [ ] **Responses**: Use `ResponseUtils.format_pagination_response()` for consistent formatting
- [ ] **Documentation**: Update `API_DOCUMENTATION.md` with new endpoint
- [ ] **Rate Limiting**: Add appropriate `@limiter.limit()` decorator
- [ ] **Authentication**: Use correct client (service vs user-authenticated)
- [ ] **Error Handling**: Wrap in try-catch with `ResponseUtils.format_error_response()`

---

## 📚 Additional Resources

- **FastAPI Best Practices**: [Official FastAPI Docs](https://fastapi.tiangolo.com/)
- **Supabase Python Client**: [Official Supabase Python Docs](https://supabase.com/docs/reference/python/)
- **Pydantic DateTime Handling**: [Pydantic DateTime Docs](https://docs.pydantic.dev/latest/concepts/types/#datetime-types)
- **Our Utility Functions**: `backend/app/core/utils.py`

---

## 🔍 Code Review Checklist

When reviewing code, ensure:
- [ ] No duplicate datetime handling patterns
- [ ] Consistent use of utility functions
- [ ] Proper error handling and response formatting
- [ ] Updated documentation
- [ ] Appropriate rate limiting
- [ ] Secure authentication patterns 