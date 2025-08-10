# Polylog 🗨️

> **Many voices, one conversation** - A real-time collaborative chat platform with AI assistance

[![React](https://img.shields.io/badge/React-18.3-blue?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green?logo=mongodb)](https://www.mongodb.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📋 Overview

Polylog is a web-based application that enables multiple users to engage in real-time conversations with an AI assistant powered by Google Cloud Platform's Language Models. The application features Google Single Sign-On authentication, WebSocket-based real-time communication, and an intelligent AI that can distinguish between user-to-user conversations and when to actively participate.

## ✨ Features

### Core Features

- 🔐 **Google SSO Authentication** - Secure login with Google accounts
- 💬 **Real-time Messaging** - WebSocket-based instant messaging
- 🤖 **Intelligent AI Assistant** - Context-aware AI participation
- 👥 **Multi-user Conversations** - Collaborative chat rooms
- 🟢 **Presence Indicators** - See who's online and typing
- 📜 **Message History** - Persistent conversation storage

### Planned Features

- 📎 File sharing capabilities
- 🎙️ Voice messages
- 📹 Video chat integration
- 👍 Message reactions
- 🔍 Advanced search
- 🌙 Dark mode

## 🏗️ Architecture

### Technology Stack

#### Frontend

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand
- **Real-time**: Socket.io Client
- **HTTP Client**: Axios
- **Routing**: React Router v7

#### Backend

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **Database**: MongoDB with Motor (async driver)
- **Cache**: Redis
- **WebSocket**: Native FastAPI WebSocket support
- **AI Integration**: Google Vertex AI (Gemini)
- **Authentication**: Google OAuth 2.0

#### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Cloud Platform**: Google Cloud Platform (GCP)
- **CDN**: Cloud CDN
- **Load Balancing**: Cloud Load Balancing

## 📁 Project Structure

```text
polylog/
├── frontend/                    # React TypeScript frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── store/             # State management
│   │   ├── types/             # TypeScript definitions
│   │   └── utils/             # Utility functions
│   └── ...
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database connections
│   │   ├── models/            # Data models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── websocket/         # WebSocket handlers
│   └── ...
├── infrastructure/              # Infrastructure configs
│   ├── docker/                # Docker configurations
│   ├── kubernetes/            # K8s manifests
│   └── terraform/             # IaC definitions
└── docs/                       # Documentation
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose
- Google Cloud account (for AI features)
- Google OAuth credentials

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/polylog.git
   cd polylog
   ```

2. **Set up environment variables**

   ```bash
   # Frontend
   cp frontend/.env.example frontend/.env
   
   # Backend
   cp backend/.env.example backend/.env
   ```

   Edit the `.env` files with your configuration:
   - Google OAuth credentials
   - GCP project details
   - MongoDB connection string
   - Secret keys

3. **Start with Docker Compose**

   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>
   - MongoDB Express: <http://localhost:8081>

### Manual Setup

#### Backend Setup

```bash
cd backend

# Using Poetry
poetry install
poetry run uvicorn app.main:app --reload

# Or using pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

#### Backend (.env)

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=polylog

# Redis
REDIS_URL=redis://localhost:6379

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Google Cloud AI
GCP_PROJECT_ID=your-project-id
VERTEX_AI_MODEL=gemini-1.5-pro
```

## 📊 Database Schema

### MongoDB Collections

#### users

```javascript
{
  _id: ObjectId,
  googleId: String,
  email: String,
  name: String,
  avatarUrl: String,
  createdAt: Date,
  updatedAt: Date
}
```

#### conversations

```javascript
{
  _id: ObjectId,
  participants: [{
    userId: ObjectId,
    joinedAt: Date
  }],
  messages: [{
    _id: ObjectId,
    userId: ObjectId,
    content: String,
    isAiMessage: Boolean,
    timestamp: Date
  }],
  lastActivity: Date
}
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Linting

To check the backend code for PEP 8 compliance, run the following command:

```bash
docker-compose exec backend poetry run flake8 .
```

## 📈 API Documentation

Once the backend is running, you can access:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

### WebSocket Events

#### Client → Server

- `message`: Send a chat message
- `typing`: Typing indicator
- `ping`: Heartbeat

#### Server → Client

- `message`: New message broadcast
- `user_joined`: User joined conversation
- `user_left`: User left conversation
- `typing`: Typing indicator broadcast
- `pong`: Heartbeat response

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Deploy with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f infrastructure/kubernetes/
```

### GCP Deployment

See [deployment guide](docs/guides/deployment.md) for detailed GCP deployment instructions.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Cloud Platform for AI services
- MongoDB for database solutions
- FastAPI and React communities
- All contributors and supporters

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/polylog/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/polylog/discussions)

## 🗺️ Roadmap

### Phase 1: MVP ✅

- [x] Basic authentication
- [x] Real-time messaging
- [x] AI integration
- [x] User presence

### Phase 2: Enhanced Features 🚧

- [ ] File sharing
- [ ] Message reactions
- [ ] Search functionality
- [ ] Conversation history

### Phase 3: Enterprise Features 📅

- [ ] Multiple rooms
- [ ] Admin dashboard
- [ ] Analytics
- [ ] API for integrations

---

<div align="center">
Made with ❤️ by the Polylog Team
</div>
