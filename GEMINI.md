## Project Overview

This is a full-stack web application called Polylog, a real-time collaborative chat platform with AI assistance.

**Frontend:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Real-time:** Socket.io Client
- **HTTP Client:** Axios
- **Routing:** React Router v6

**Backend:**
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** MongoDB with Motor (async driver)
- **Cache:** Redis
- **WebSocket:** Native FastAPI WebSocket support
- **AI Integration:** Google Vertex AI (Gemini)
- **Authentication:** Google OAuth 2.0

**Infrastructure:**
- **Containerization:** Docker & Docker Compose

## Building and Running

### With Docker (Recommended)

1.  **Set up environment variables:**
    ```bash
    # Frontend
    cp frontend/.env.example frontend/.env

    # Backend
    cp backend/.env.example backend/.env
    ```
    *Edit the `.env` files with your configuration.*

2.  **Start with Docker Compose:**
    ```bash
    docker-compose up -d
    ```

3.  **Access the application:**
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Development Conventions

### Testing

#### Backend
```bash
cd backend
pytest
```

#### Frontend
```bash
cd frontend
npm run test
```

### API Documentation

API documentation is available via Swagger UI and ReDoc when the backend is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
