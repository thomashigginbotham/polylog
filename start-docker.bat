@echo off
echo 🚀 Starting Polylog with Docker Compose (Vertex AI Integrated)...
echo.

REM Check if we're in the project root directory
if not exist "docker-compose.yml" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Make sure you're in the directory containing docker-compose.yml
    pause
    exit /b 1
)

REM Check if Docker is running
docker info > nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running
    echo    Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if the service account key file exists
if not exist "backend\google-credentials.json" (
    echo ❌ Error: Google Cloud service account key not found!
    echo    Expected: backend\google-credentials.json
    echo    Make sure you've placed your service account key in the backend directory
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo ❌ Error: Backend .env file not found!
    echo    Make sure backend\.env exists with proper configuration
    pause
    exit /b 1
)

echo ✅ Pre-flight checks passed
echo.

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start all services
echo 🏗️  Building and starting all services...
docker-compose up --build -d

if errorlevel 1 (
    echo ❌ Failed to start services
    echo.
    echo 📋 Checking logs for errors...
    docker-compose logs --tail=20
    pause
    exit /b 1
)

echo.
echo ✅ Polylog is starting up! Services will be available at:
echo 🌐 Frontend:         http://localhost:3000
echo 🔗 Backend API:      http://localhost:8000
echo 📚 API Docs:         http://localhost:8000/docs
echo 🧪 WebSocket Test:   http://localhost:8000/ws-test  
echo 🤖 AI Test:          POST http://localhost:8000/api/v1/test-ai
echo 🗄️  MongoDB Admin:   http://localhost:8081 (admin/admin123)
echo.

REM Wait a moment for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak > nul

REM Check service health
echo 🏥 Checking service health...

REM Test backend health
curl -s http://localhost:8000/health > nul
if errorlevel 1 (
    echo ⚠️  Backend might still be starting up...
) else (
    echo ✅ Backend is responding
)

REM Test AI integration
curl -s -X POST http://localhost:8000/api/v1/test-ai > nul
if errorlevel 1 (
    echo ⚠️  AI service check failed - might still be initializing...
) else (
    echo ✅ AI service is responding
)

echo.
echo 🎉 Polylog is ready!
echo.
echo 💡 Next steps:
echo    1. Open http://localhost:3000 to access the app
echo    2. Test AI: curl -X POST http://localhost:8000/api/v1/test-ai
echo    3. View logs: docker-compose logs -f
echo    4. Stop services: docker-compose down
echo.

REM Ask if user wants to follow logs
set /p follow_logs="📜 Do you want to follow the logs? (y/n): "
if /i "%follow_logs%"=="y" (
    echo.
    echo 📜 Following logs (Ctrl+C to exit)...
    docker-compose logs -f
)

pause
