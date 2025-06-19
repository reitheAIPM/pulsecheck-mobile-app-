#!/bin/bash
source /opt/venv/bin/activate
cd backend
export PORT=${PORT:-8000}
python main.py 