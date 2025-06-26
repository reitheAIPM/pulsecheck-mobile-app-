#!/usr/bin/env python3
"""
Debug Middleware Test Script
Tests if the debug middleware can be imported and functions correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_middleware_import():
    """Test if middleware can be imported"""
    try:
        from app.middleware.debug_middleware import DebugMiddleware, debug_store, get_debug_summary
        print("✅ Debug middleware imported successfully")
        print(f"✅ Debug store type: {type(debug_store).__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import debug middleware: {e}")
        return False

def test_debug_store_functionality():
    """Test basic debug store functionality"""
    try:
        from app.middleware.debug_middleware import debug_store
        
        # Test basic attributes
        print(f"✅ Debug store has requests: {hasattr(debug_store, 'requests')}")
        print(f"✅ Debug store has responses: {hasattr(debug_store, 'responses')}")
        print(f"✅ Debug store has database_ops: {hasattr(debug_store, 'database_ops')}")
        
        # Test methods
        recent = debug_store.get_recent_requests(5)
        print(f"✅ get_recent_requests works: {len(recent)} requests")
        
        errors = debug_store.get_error_requests(5)
        print(f"✅ get_error_requests works: {len(errors)} errors")
        
        db_stats = debug_store.get_database_stats(60)
        print(f"✅ get_database_stats works: {type(db_stats)}")
        
        # Test enhanced risk analysis
        risk = debug_store.get_enhanced_risk_analysis(60)
        print(f"✅ get_enhanced_risk_analysis works: {risk.get('overall_risk_level', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Debug store functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_summary():
    """Test debug summary function"""
    try:
        from app.middleware.debug_middleware import get_debug_summary
        
        summary = get_debug_summary()
        print("✅ get_debug_summary works")
        print(f"   Recent requests: {len(summary.get('recent_requests', []))}")
        print(f"   Error requests: {len(summary.get('error_requests', []))}")
        print(f"   Store stats: {summary.get('store_stats', {})}")
        
        return True
    except Exception as e:
        print(f"❌ Debug summary test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Debug Middleware Functionality")
    print("=" * 50)
    
    tests = [
        ("Middleware Import", test_middleware_import),
        ("Debug Store Functionality", test_debug_store_functionality),
        ("Debug Summary", test_debug_summary)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Debug middleware is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 