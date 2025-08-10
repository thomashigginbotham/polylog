#!/bin/bash

echo "🚀 Starting Polylog with Docker Compose (Vertex AI Integrated)..."
echo ""

# Check if we're in the project root directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Make sure you're in the directory containing docker-compose.yml"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

# Check if the service account key file exists
if [ ! -f "backend/google-credentials.json" ]; then
    echo "❌ Error: Google Cloud service account key not found!"
    echo "   Expected: backend/google-credentials.json"
    echo "   Make sure you've placed your service account key in the backend directory"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: Backend .env file not found!"
    echo "   Make sure backend/.env exists with proper configuration"
    exit 1
fi

echo "✅ Pre-flight checks passed"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    echo ""
    echo "📋 Checking logs for errors..."
    docker-compose logs --tail=20
    exit 1
fi

echo ""
echo "✅ Polylog is starting up! Services will be available at:"
echo "🌐 Frontend:         http://localhost:3000"
echo "🔗 Backend API:      http://localhost:8000"
echo "📚 API Docs:         http://localhost:8000/docs"
echo "🧪 WebSocket Test:   http://localhost:8000/ws-test"
echo "🤖 AI Test:          POST http://localhost:8000/api/v1/test-ai"
echo "🗄️  MongoDB Admin:   http://localhost:8081 (admin/admin123)"
echo ""

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo "🏥 Checking service health..."

# Test backend health
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Backend is responding"
else
    echo "⚠️  Backend might still be starting up..."
fi

# Test AI integration
if curl -s -X POST http://localhost:8000/api/v1/test-ai >/dev/null; then
    echo "✅ AI service is responding"
else
    echo "⚠️  AI service check failed - might still be initializing..."
fi

echo ""
echo "🎉 Polylog is ready!"
echo ""
echo "💡 Next steps:"
echo "   1. Open http://localhost:3000 to access the app"
echo "   2. Test AI: curl -X POST http://localhost:8000/api/v1/test-ai"
echo "   3. View logs: docker-compose logs -f"
echo "   4. Stop services: docker-compose down"
echo ""

# Ask if user wants to follow logs
read -p "📜 Do you want to follow the logs? (y/n): " follow_logs
if [[ $follow_logs =~ ^[Yy]$ ]]; then
    echo ""
    echo "📜 Following logs (Ctrl+C to exit)..."
    docker-compose logs -f
fi
