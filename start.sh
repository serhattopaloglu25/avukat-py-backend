#!/bin/bash

echo "🚀 Starting AA-PY Backend..."

# Run migrations
echo "📦 Running database migrations..."
alembic upgrade head || echo "⚠️ Migration failed, continuing..."

# Start the application
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
