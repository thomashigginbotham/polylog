#!/bin/bash

echo "🚀 Starting Polylog backend with Vertex AI integration..."

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if the JSON key file exists
if [ ! -f "polylog-dev-1a5218d3b932.json" ]; then
    echo "⚠️  Warning: Google Cloud service account key not found!"
    echo "    Make sure polylog-dev-1a5218d3b932.json exists in the backend directory"
fi

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check environment variables
echo "🔧 Checking configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  Warning: .env file not found - using defaults"
fi

# Start the server
echo "🌐 Starting FastAPI server..."
echo ""
echo "🔗 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo "🧪 WebSocket test page: http://localhost:8000/ws-test"
echo "🤖 AI test endpoint: POST http://localhost:8000/api/v1/test-ai"
echo ""

python -m app.main

