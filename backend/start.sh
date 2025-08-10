#!/bin/sh

# Simple startup script for debugging
echo "Starting Polylog backend..."
echo "MongoDB URL: ${MONGODB_URL}"
echo "Redis URL: ${REDIS_URL}"
echo "Debug mode: ${DEBUG}"

# Start the application
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
