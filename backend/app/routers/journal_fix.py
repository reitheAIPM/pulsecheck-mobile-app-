"""
Temporary fix for journal entry creation bug
This bypasses rate limiting to test if that's causing the timeout
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
import uuid
from datetime import datetime, timezone
import logging
import json

from app.models.journal import JournalEntryCreate, JournalEntryResponse
from app.core.database import get_database, Database
from app.core.security import get_current_user_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Journal Fix"])

@router.post("/journal-fix/test-create")
async def test_create_journal_entry_no_rate_limit(
    request: Request,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Test journal entry creation without rate limiting
    This endpoint manually parses JSON to bypass potential issues
    """
    try:
        # Manually get request body
        body = await request.body()
        
        if not body:
            return {"error": "No request body", "debug": "Body is empty"}
        
        # Parse JSON manually
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            return {
                "error": "JSON decode error",
                "details": str(e),
                "raw_body": body[:100].decode('utf-8', errors='ignore')
            }
        
        # Validate required fields
        required_fields = ["content", "mood_level", "energy_level", "stress_level"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return {
                "error": "Missing required fields",
                "missing": missing_fields,
                "received": list(data.keys())
            }
        
        # Create journal entry manually
        try:
            entry = JournalEntryCreate(**data)
        except Exception as e:
            return {
                "error": "Model validation error",
                "details": str(e),
                "data": data
            }
        
        # Create entry in database
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": entry.content,
            "mood_level": entry.mood_level,
            "energy_level": entry.energy_level,
            "stress_level": entry.stress_level,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into database
        client = db.get_client()
        result = client.table("journal_entries").insert(entry_data).execute()
        
        if result.data:
            return {
                "success": True,
                "entry_id": result.data[0]["id"],
                "message": "Journal entry created successfully without rate limiting",
                "debug_info": {
                    "rate_limiting": "bypassed",
                    "json_parsing": "manual",
                    "model_validation": "success"
                }
            }
        else:
            return {
                "error": "Database insertion failed",
                "result": str(result)
            }
            
    except Exception as e:
        logger.error(f"Error in test create: {e}")
        return {
            "error": "Unexpected error",
            "type": type(e).__name__,
            "details": str(e)
        }

@router.post("/journal-fix/test-original-with-logging")
async def test_original_endpoint_with_logging(
    request: Request,
    entry: JournalEntryCreate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Test the original endpoint pattern but with extensive logging
    """
    logger.info("=== JOURNAL FIX: Starting request processing ===")
    logger.info(f"User: {current_user.get('id')}")
    logger.info(f"Entry data: {entry.dict()}")
    
    try:
        # Log each step
        logger.info("Step 1: Creating entry data")
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": entry.content,
            "mood_level": entry.mood_level,
            "energy_level": entry.energy_level,
            "stress_level": entry.stress_level,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        logger.info("Step 2: Entry data created successfully")
        
        logger.info("Step 3: Getting database client")
        client = db.get_client()
        logger.info("Step 4: Database client obtained")
        
        logger.info("Step 5: Inserting into database")
        result = client.table("journal_entries").insert(entry_data).execute()
        logger.info(f"Step 6: Database result: {result.data is not None}")
        
        if result.data:
            return JournalEntryResponse(**result.data[0])
        else:
            raise HTTPException(status_code=500, detail="Database insertion failed")
            
    except Exception as e:
        logger.error(f"=== JOURNAL FIX: Error occurred: {type(e).__name__}: {e} ===")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/journal-fix/test-rate-limiter")
async def test_rate_limiter_status():
    """
    Check if rate limiter is causing issues
    """
    from app.core.security import limiter
    
    return {
        "rate_limiter_info": {
            "type": type(limiter).__name__,
            "key_func": str(limiter.key_func) if hasattr(limiter, 'key_func') else "unknown",
            "message": "Rate limiter is configured"
        },
        "test_info": {
            "purpose": "Testing if rate limiter is causing journal creation timeout",
            "recommendation": "Use /api/v1/journal-fix/test-create to bypass rate limiting"
        }
    } 