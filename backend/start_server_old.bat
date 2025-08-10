@echo off
echo 🚀 Starting Polylog backend with Vertex AI integration...

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo ❌ Error: Please run this script from the backend directory
    pause
    exit /b 1
)

REM Check if the JSON key file exists
if not exist "polylog-dev-1a5218d3b932.json" (
    echo ⚠️  Warning: Google Cloud service account key not found!
    echo    Make sure polylog-dev-1a5218d3b932.json exists in the backend directory
    echo.
)

REM Install/update dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check environment variables
echo 🔧 Checking configuration...
if exist ".env" (
    echo ✅ .env file found
) else (
    echo ⚠️  Warning: .env file not found - using defaults
)

REM Start the server
echo 🌐 Starting FastAPI server...
echo.
echo 🔗 Server will be available at: http://localhost:8000
echo 📚 API docs will be available at: http://localhost:8000/docs
echo 🧪 WebSocket test page: http://localhost:8000/ws-test
echo 🤖 AI test endpoint: POST http://localhost:8000/api/v1/test-ai
echo.

python -m app.main
pause
