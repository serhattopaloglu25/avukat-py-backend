#!/bin/bash

echo "🚀 Starting AA-PY Backend Deployment..."

# Check if environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo "❌ JWT_SECRET not set"
    exit 1
fi

# Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Start the application
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
