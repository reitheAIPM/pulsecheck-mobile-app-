#!/usr/bin/env python3
"""
Trigger API requests and capture Railway logs
"""
import subprocess
import time
import json
import sys

def trigger_api_requests():
    """Trigger various API requests to generate log activity"""
    print("🔁 Triggering API requests to generate log activity...")
    
    base_url = "https://pulsecheck-mobile-app-production.up.railway.app"
    
    # List of requests to make
    requests = [
        # Basic health check
        f'curl.exe -s "{base_url}/" -w "\\n"',
        
        # Try debug endpoints (these should generate logs even if they 404)
        f'curl.exe -s "{base_url}/api/v1/debug/summary" -w "\\n"',
        f'curl.exe -s "{base_url}/api/v1/debug/requests" -w "\\n"',
        f'curl.exe -s "{base_url}/api/v1/debug/ai-insights/comprehensive" -w "\\n"',
        
        # Try working endpoints
        f'curl.exe -s "{base_url}/api/v1/adaptive-ai/health" -w "\\n"',
        
        # Try auth endpoint with test data
        f'''curl.exe -X POST "{base_url}/auth/signin" -H "Content-Type: application/json" -d "{{\\"email\\":\\"test@example.com\\",\\"password\\":\\"test123\\"}}" -w "\\n"''',
    ]
    
    for i, request in enumerate(requests, 1):
        print(f"🔄 Request {i}/{len(requests)}: {request}")
        try:
            result = subprocess.run(request, shell=True, capture_output=True, text=True, timeout=10)
            print(f"✅ Response: {result.stdout[:100]}...")
            if result.stderr:
                print(f"⚠️  Error: {result.stderr[:100]}...")
        except subprocess.TimeoutExpired:
            print(f"⏰ Request {i} timed out")
        except Exception as e:
            print(f"❌ Request {i} failed: {e}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("✅ All API requests completed!")

def capture_railway_logs():
    """Capture Railway logs for 10 seconds"""
    print("🔁 Capturing Railway logs...")
    
    try:
        # Run railway logs with timeout
        result = subprocess.run(
            ["railway", "logs", "--service", "pulsecheck-mobile-app-"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("📊 Railway Logs Output:")
        print("=" * 50)
        print(result.stdout)
        print("=" * 50)
        
        if result.stderr:
            print("⚠️  Railway Logs Errors:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Log capture completed (10 second timeout)")
    except Exception as e:
        print(f"❌ Failed to capture logs: {e}")

def main():
    """Main execution flow"""
    print("🚀 Starting API request trigger and log capture...")
    print()
    
    # Step 1: Trigger API requests
    trigger_api_requests()
    print()
    
    # Step 2: Small delay to let logs propagate
    print("⏳ Waiting 2 seconds for logs to propagate...")
    time.sleep(2)
    print()
    
    # Step 3: Capture logs
    capture_railway_logs()
    
    print("🎉 Workflow completed!")

if __name__ == "__main__":
    main() 