#!/bin/bash
echo "Starting simple API..."
uvicorn simple_main:app --host 0.0.0.0 --port ${PORT:-8000}
