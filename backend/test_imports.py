#!/usr/bin/env python3
"""
Quick test script to verify imports work locally
"""

try:
    print("🧪 Testing imports...")
    
    print("📦 Testing journal router import...")
    from app.routers import journal
    print("✅ Journal router imported successfully")
    
    print("📦 Testing main app import...")
    from app.routers import auth, checkins, journal
    print("✅ All routers imported successfully")
    
    print("📦 Testing database import...")
    from app.core.database import get_database
    print("✅ Database import successful")
    
    print("📦 Testing config import...")
    from app.core.config import settings
    print("✅ Config import successful")
    
    print("🎉 All imports working locally!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc() 