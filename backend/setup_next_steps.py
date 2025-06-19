#!/usr/bin/env python3
"""
PulseCheck Next Steps Setup Guide
================================

This script guides you through the next development steps to get PulseCheck
fully operational with database integration and API testing.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step_num, title, description=""):
    """Print a formatted step."""
    print(f"\n{step_num}. {title}")
    if description:
        print(f"   {description}")

def check_file_exists(filepath):
    """Check if a file exists."""
    return Path(filepath).exists()

def generate_secret_key():
    """Generate a secure secret key for JWT."""
    return secrets.token_hex(32)

def main():
    print_header("PulseCheck Next Steps Setup Guide")
    
    print("\n🎯 Current Status: Foundation Complete, Ready for Integration")
    print("✅ Backend: FastAPI with 7 API endpoints")
    print("✅ Frontend: React Native with navigation")
    print("✅ AI Integration: Pulse personality system")
    print("✅ Testing: All offline tests passing")
    
    print_header("Next Steps to Complete Setup")
    
    # Step 1: Environment Configuration
    print_step(1, "Configure Environment Variables", 
               "Set up API keys and database credentials")
    
    env_file = Path(".env")
    if env_file.exists():
        print("   ⚠️  .env file already exists. Please review and update if needed.")
    else:
        print("   📝 Creating .env file from template...")
        if check_file_exists("env.example"):
            subprocess.run(["copy", "env.example", ".env"], shell=True)
            print("   ✅ .env file created from template")
        else:
            print("   ❌ env.example not found")
    
    print("\n   🔑 Required API Keys to Configure:")
    print("   - SUPABASE_URL: Your Supabase project URL")
    print("   - SUPABASE_KEY: Your Supabase anon key")
    print("   - SUPABASE_SERVICE_KEY: Your Supabase service key")
    print("   - OPENAI_API_KEY: Your OpenAI API key")
    print("   - SECRET_KEY: JWT secret (auto-generated)")
    
    # Generate a secret key
    secret_key = generate_secret_key()
    print(f"\n   🔐 Generated SECRET_KEY: {secret_key}")
    
    # Step 2: Supabase Setup
    print_step(2, "Set Up Supabase Database", 
               "Create project and configure database schema")
    
    print("\n   🌐 Supabase Setup Instructions:")
    print("   1. Go to https://supabase.com")
    print("   2. Create a new project")
    print("   3. Note your project URL and API keys")
    print("   4. Run: python create_database_schema.py")
    
    # Step 3: Database Schema
    print_step(3, "Create Database Schema", 
               "Set up tables for users, check-ins, and AI insights")
    
    if check_file_exists("create_database_schema.py"):
        print("   📋 Database schema script ready")
        print("   💡 Run: python create_database_schema.py")
    else:
        print("   ❌ create_database_schema.py not found")
    
    # Step 4: Test Backend
    print_step(4, "Test Backend with Database", 
               "Verify all endpoints work with real database")
    
    print("\n   🧪 Testing Commands:")
    print("   - Start server: uvicorn main:app --reload")
    print("   - Test health: curl http://localhost:8000/health")
    print("   - View docs: http://localhost:8000/docs")
    
    # Step 5: Frontend Enhancement
    print_step(5, "Enhance Frontend", 
               "Add Builder.io integration and testing framework")
    
    print("\n   📱 Frontend Enhancement Tasks:")
    print("   - Add Builder.io dependencies")
    print("   - Set up component registry")
    print("   - Add Jest + React Native Testing Library")
    print("   - Configure ESLint and Prettier")
    
    # Step 6: End-to-End Testing
    print_step(6, "End-to-End Integration Testing", 
               "Test complete user flow")
    
    print("\n   🔄 Integration Test Flow:")
    print("   1. User registration/login")
    print("   2. Submit daily check-in")
    print("   3. Receive AI insights")
    print("   4. View progress dashboard")
    
    # Step 7: Deployment
    print_step(7, "Deploy to Production", 
               "Deploy backend to Railway")
    
    print("\n   🚀 Deployment Steps:")
    print("   1. Create Railway account")
    print("   2. Connect GitHub repository")
    print("   3. Configure environment variables")
    print("   4. Deploy and test production endpoints")
    
    print_header("Immediate Action Items")
    
    print("\n🎯 PRIORITY 1: Database Setup")
    print("1. Get Supabase API keys")
    print("2. Update .env file with credentials")
    print("3. Run database schema creation")
    print("4. Test backend with real database")
    
    print("\n🎯 PRIORITY 2: API Testing")
    print("1. Test user registration")
    print("2. Test check-in submission")
    print("3. Test AI response generation")
    print("4. Verify data persistence")
    
    print("\n🎯 PRIORITY 3: Frontend Integration")
    print("1. Add Builder.io to frontend")
    print("2. Test mobile app connectivity")
    print("3. Implement error handling")
    print("4. Add loading states")
    
    print_header("Success Criteria")
    
    print("\n✅ Ready for User Testing When:")
    print("- Backend API responds to all endpoints")
    print("- Database stores and retrieves data correctly")
    print("- AI generates helpful, consistent responses")
    print("- Mobile app connects to backend successfully")
    print("- Complete user flow works end-to-end")
    
    print_header("Getting Help")
    
    print("\n📚 Documentation:")
    print("- API Reference: ai/api-endpoints.md")
    print("- Setup Guide: ai/development-setup-guide.md")
    print("- Frontend Guide: ai/frontend-development-guide.md")
    print("- Progress Tracking: ai/progress-highlights.md")
    
    print("\n🔧 Troubleshooting:")
    print("- Check environment variables are set correctly")
    print("- Verify Supabase credentials and permissions")
    print("- Test database connection separately")
    print("- Check API response logs for errors")
    
    print("\n" + "="*60)
    print("  🚀 Ready to continue development!")
    print("="*60)

if __name__ == "__main__":
    main() 