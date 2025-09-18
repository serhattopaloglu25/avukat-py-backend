#!/bin/bash

echo "🚀 Starting AA-PY Backend (No Migrations)..."

# Start the application directly
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
