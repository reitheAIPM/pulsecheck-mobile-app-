#!/usr/bin/env python3
"""
PulseCheck v2.0.0 Enhanced Debug Startup Script
Forces Railway to rebuild by creating a new entry point
"""

print("🚀 STARTUP V2: PulseCheck Enhanced Debug System Loading...")

# Import the main app
from main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    print("🚀 STARTUP V2: Starting uvicorn server...")
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 