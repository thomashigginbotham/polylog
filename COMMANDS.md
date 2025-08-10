# Polylog - Quick Command Reference

## 🚀 Start/Stop
```bash
# Quick start (Windows)
start-docker.bat

# Quick start (Linux/Mac)  
./start-docker.sh

# Manual start
docker-compose up -d

# Stop all services
docker-compose down
```

## 🧪 Testing
```bash
# Test AI integration
curl -X POST http://localhost:8000/api/v1/test-ai

# Test backend health
curl http://localhost:8000/health

# WebSocket test page
open http://localhost:8000/ws-test
```

## 📜 Logs & Debugging
```bash
# Follow all logs
docker-compose logs -f

# Backend logs only
docker-compose logs -f backend

# Check container status
docker-compose ps

# Access backend shell
docker-compose exec backend bash

# Test AI in container
docker-compose exec backend python -c "
from app.services.ai_service import ai_service
import asyncio
asyncio.run(ai_service.initialize())
print('AI Available:', ai_service.is_available)
"
```

## 🔄 Rebuilding
```bash
# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Rebuild single service
docker-compose build backend
docker-compose up -d backend
```

## 📍 URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:8000  
- API Docs: http://localhost:8000/docs
- MongoDB Admin: http://localhost:8081 (admin/admin123)
- WebSocket Test: http://localhost:8000/ws-test

## 🐛 Common Fixes
```bash
# AI not working - check credentials
docker-compose exec backend ls -la google-credentials.json

# Anonymous user - check auth logs  
docker-compose logs backend | grep -i auth

# Clean restart everything
docker-compose down -v
docker system prune -f
docker-compose up --build -d
```
