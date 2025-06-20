#!/bin/bash
# Navigate to the backend directory where main.py is located
cd backend

# Start the uvicorn server directly
# This is a more robust way to run in production environments
# Railway provides the $PORT variable automatically
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} 