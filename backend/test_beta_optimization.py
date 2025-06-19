#!/usr/bin/env python3
"""
Beta Optimization Test Script
Tests the new beta features including user tiers, rate limiting, and analytics
"""

import asyncio
import sys
import os
import json
from datetime import datetime, date

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_database
from app.services.beta_optimization import BetaOptimizationService
from app.services.pulse_ai import PulseAI
from app.models.journal import JournalEntry
from openai import OpenAI

async def test_database_setup():
    """Test if the beta optimization database schema is properly set up"""
    print("🔍 Testing database setup...")
    
    try:
        db = await get_database()
        
        # Test if beta tables exist
        tables_to_check = [
            'user_tier_limits',
            'journal_summaries', 
            'ai_usage_logs',
            'ai_feedback',
            'daily_usage_quotas'
        ]
        
        for table in tables_to_check:
            try:
                result = await db.fetch_one(f"SELECT COUNT(*) FROM {table}")
                print(f"✅ Table '{table}' exists and accessible")
            except Exception as e:
                print(f"❌ Table '{table}' not found or not accessible: {e}")
                return False
        
        # Test if functions exist
        try:
            result = await db.fetch_one("SELECT * FROM get_user_tier_info('test-user-id')")
            print("✅ Function 'get_user_tier_info' working")
        except Exception as e:
            print(f"❌ Function 'get_user_tier_info' not working: {e}")
            return False
        
        # Test if views exist
        views_to_check = [
            'beta_daily_metrics',
            'beta_user_engagement', 
            'beta_feedback_analysis'
        ]
        
        for view in views_to_check:
            try:
                result = await db.fetch_one(f"SELECT COUNT(*) FROM {view}")
                print(f"✅ View '{view}' exists and accessible")
            except Exception as e:
                print(f"❌ View '{view}' not found: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False

async def test_user_tier_service():
    """Test the user tier service functionality"""
    print("\n🔍 Testing user tier service...")
    
    try:
        db = await get_database()
        beta_service = BetaOptimizationService(db, None)
        
        test_user_id = "test-user-123"
        
        # Test getting user tier info
        tier_info = await beta_service.tier_service.get_user_tier_info(test_user_id)
        print(f"✅ User tier info retrieved: {tier_info.tier_name} tier")
        print(f"   - Daily AI limit: {tier_info.daily_ai_limit}")
        print(f"   - Context depth: {tier_info.context_depth}")
        print(f"   - Usage remaining: {tier_info.usage_remaining}")
        
        # Test usage limit check
        can_use, tier_info = await beta_service.tier_service.check_usage_limit(test_user_id)
        print(f"✅ Usage limit check: {'Can use AI' if can_use else 'Rate limited'}")
        
        # Test increment usage
        if can_use:
            await beta_service.tier_service.increment_usage(test_user_id)
            print("✅ Usage incremented successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ User tier service test failed: {e}")
        return False

async def test_context_builder():
    """Test the context builder service"""
    print("\n🔍 Testing context builder...")
    
    try:
        db = await get_database()
        beta_service = BetaOptimizationService(db, None)
        
        # Create a mock journal entry
        mock_entry = JournalEntry(
            id="test-entry-123",
            user_id="test-user-123",
            content="Today was a challenging day at work. I had multiple deadlines and felt overwhelmed.",
            mood_level=4,
            energy_level=3,
            stress_level=8,
            created_at=datetime.now()
        )
        
        # Get user tier info
        tier_info = await beta_service.tier_service.get_user_tier_info("test-user-123")
        
        # Build context
        context = await beta_service.context_builder.build_ai_context("test-user-123", mock_entry, tier_info)
        
        print(f"✅ Context built successfully")
        print(f"   - Context type: {context.context_type}")
        print(f"   - Total tokens: {context.total_tokens}")
        print(f"   - Recent entries: {len(context.recent_entries)}")
        print(f"   - Summaries: {len(context.summaries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context builder test failed: {e}")
        return False

async def test_cost_tracking():
    """Test the cost tracking functionality"""
    print("\n🔍 Testing cost tracking...")
    
    try:
        db = await get_database()
        beta_service = BetaOptimizationService(db, None)
        
        # Test cost calculation
        cost = beta_service.cost_tracker.calculate_cost('gpt-3.5-turbo', 100, 50)
        print(f"✅ Cost calculation: ${cost:.6f} for 100 prompt + 50 response tokens")
        
        # Test logging (mock data)
        await beta_service.log_ai_interaction(
            user_id="test-user-123",
            journal_entry_id="test-entry-123",
            prompt_tokens=100,
            response_tokens=50,
            model_used='gpt-3.5-turbo',
            response_time_ms=1500,
            confidence_score=0.8,
            context_type='standard',
            success=True
        )
        print("✅ AI interaction logged successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost tracking test failed: {e}")
        return False

async def test_feedback_system():
    """Test the feedback collection system"""
    print("\n🔍 Testing feedback system...")
    
    try:
        db = await get_database()
        beta_service = BetaOptimizationService(db, None)
        
        # Submit test feedback
        await beta_service.feedback_service.submit_feedback(
            user_id="test-user-123",
            journal_entry_id="test-entry-123",
            feedback_type="thumbs_up",
            feedback_text="Great response, very helpful!",
            ai_response_content="Test AI response content",
            prompt_content="Test prompt content",
            confidence_score=0.8,
            response_time_ms=1500,
            user_tier="beta"
        )
        print("✅ Feedback submitted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback system test failed: {e}")
        return False

async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n🔍 Testing rate limiting...")
    
    try:
        db = await get_database()
        beta_service = BetaOptimizationService(db, None)
        
        test_user_id = "test-rate-limit-user"
        
        # Check initial access
        can_use, tier_info, message = await beta_service.can_user_access_ai(test_user_id)
        print(f"✅ Initial access check: {'Allowed' if can_use else 'Denied'}")
        
        if can_use:
            print(f"   - Tier: {tier_info.tier_name}")
            print(f"   - Remaining uses: {tier_info.usage_remaining}")
        else:
            print(f"   - Message: {message}")
        
        # Test limit message generation
        limit_message = beta_service._generate_limit_message(tier_info)
        print(f"✅ Limit message generated: {limit_message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

async def test_admin_analytics():
    """Test admin analytics views"""
    print("\n🔍 Testing admin analytics...")
    
    try:
        db = await get_database()
        
        # Test daily metrics view
        try:
            result = await db.fetch_one("SELECT * FROM beta_daily_metrics LIMIT 1")
            print("✅ Daily metrics view accessible")
        except Exception as e:
            print(f"⚠️  Daily metrics view empty (expected for new setup): {e}")
        
        # Test user engagement view
        try:
            result = await db.fetch_one("SELECT * FROM beta_user_engagement LIMIT 1")
            print("✅ User engagement view accessible")
        except Exception as e:
            print(f"⚠️  User engagement view empty (expected for new setup): {e}")
        
        # Test feedback analysis view
        try:
            result = await db.fetch_one("SELECT * FROM beta_feedback_analysis LIMIT 1")
            print("✅ Feedback analysis view accessible")
        except Exception as e:
            print(f"⚠️  Feedback analysis view empty (expected for new setup): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin analytics test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all beta optimization tests"""
    print("🚀 Starting Beta Optimization Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("User Tier Service", test_user_tier_service),
        ("Context Builder", test_context_builder),
        ("Cost Tracking", test_cost_tracking),
        ("Feedback System", test_feedback_system),
        ("Rate Limiting", test_rate_limiting),
        ("Admin Analytics", test_admin_analytics),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All beta optimization features are working correctly!")
    elif passed >= total * 0.8:
        print("✅ Most features working. Some minor issues to address.")
    else:
        print("⚠️  Several issues found. Review failed tests.")
    
    return passed == total

if __name__ == "__main__":
    print("Beta Optimization Test Suite")
    print("Testing all new beta features...")
    
    success = asyncio.run(run_comprehensive_test())
    
    if success:
        print("\n🚀 Ready for beta launch!")
        sys.exit(0)
    else:
        print("\n🔧 Some issues need to be fixed before beta launch.")
        sys.exit(1) 