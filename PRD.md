# Product Requirements Document: Polylog

## Document Information
- **Product Name:** Polylog
- **Version:** 1.2
- **Date:** August 9, 2025
- **Status:** Draft
- **Author:** Product Team

---

## 1. Executive Summary

Polylog is a web-based application that enables multiple users to engage in real-time conversations with an AI assistant powered by Google Cloud Platform's Language Models. The application features Google Single Sign-On authentication, WebSocket-based real-time communication, and an intelligent AI that can distinguish between user-to-user conversations and when to actively participate.

### Key Features
- Multi-user collaborative chat interface
- AI assistant with contextual awareness
- Google SSO authentication
- Real-time notifications and presence indicators
- Modern, responsive UI design
- Cloud-native architecture on GCP

---

## 2. Product Overview

### 2.1 Problem Statement
Teams and groups often need to collaborate with AI assistance but lack platforms that support multi-user conversations where the AI can intelligently participate without dominating the discussion.

### 2.2 Solution
Polylog provides a shared space where multiple users can interact with each other and an AI assistant that understands social dynamics and knows when to contribute versus when to observe.

**Product Name Rationale:** "Polylog" combines "poly" (many) with "log" (dialogue, chat log), representing the multi-participant nature of conversations and the persistent logging of collaborative discussions.

### 2.3 Target Audience
- Small to medium-sized teams
- Project groups requiring AI assistance
- Educational groups and study teams
- Creative collaborators

---

## 3. Goals and Objectives

### 3.1 Business Goals
- Create a differentiated collaborative AI experience
- Establish a foundation for team-based AI interactions
- Build a scalable platform for future enterprise features

### 3.2 User Goals
- Enable seamless collaboration between humans and AI
- Reduce context switching between communication tools
- Improve team productivity with intelligent AI assistance

### 3.3 Success Criteria
- User engagement: Average session duration > 10 minutes
- User retention: 60% monthly active user retention
- Performance: Message delivery latency < 200ms
- Availability: 99.9% uptime

---

## 4. User Stories and Use Cases

### 4.1 Primary User Stories

**US-001: User Authentication**
- As a user, I want to log in with my Google account so that I can quickly access the chat without creating new credentials.

**US-002: Join Conversation**
- As a user, I want to join an existing conversation and see the full history so that I understand the context.

**US-003: Real-time Messaging**
- As a user, I want to send messages that appear instantly to all participants so that we can have natural conversations.

**US-004: AI Interaction**
- As a user, I want the AI to help when asked but not interrupt user-to-user conversations unnecessarily.

**US-005: Presence Awareness**
- As a user, I want to see who is currently in the conversation so that I know who I'm talking with.

### 4.2 Detailed Use Case Flow

**UC-001: Initial User Onboarding**
1. User navigates to application URL
2. System redirects to login page
3. User clicks "Sign in with Google"
4. Google OAuth flow completes
5. System creates/retrieves user profile
6. User enters main chat interface
7. AI sends personalized welcome message

**UC-002: Multi-user Conversation Flow**
1. First user asks AI for assistance
2. AI provides helpful response
3. Second user joins conversation
4. System notifies all users of new participant
5. AI summarizes conversation for new user
6. Users engage in peer-to-peer discussion
7. AI monitors but doesn't interrupt
8. After pause, AI offers assistance if relevant

---

## 5. Functional Requirements

### 5.1 Authentication & Authorization
- **FR-001:** Support Google OAuth 2.0 for authentication
- **FR-002:** Maintain user sessions with JWT tokens
- **FR-003:** Support logout functionality
- **FR-004:** Handle token refresh automatically

### 5.2 Chat Interface
- **FR-005:** Display message history with timestamps
- **FR-006:** Show user avatars and names
- **FR-007:** Support text input with Enter to send
- **FR-008:** Display typing indicators
- **FR-009:** Auto-scroll to latest messages
- **FR-010:** Support message formatting (basic markdown)

### 5.3 Real-time Communication
- **FR-011:** Establish WebSocket connection on login
- **FR-012:** Broadcast messages to all connected users
- **FR-013:** Send presence updates (join/leave/typing)
- **FR-014:** Handle connection recovery
- **FR-015:** Queue messages during disconnection
- **FR-016:** Use MongoDB Change Streams for real-time updates
- **FR-017:** Implement optimistic UI updates with rollback

### 5.4 AI Integration
- **FR-018:** Connect to GCP Vertex AI or similar LLM service
- **FR-019:** Maintain conversation context across messages
- **FR-020:** Implement smart response triggers:
  - Direct mentions (@AI or similar)
  - Questions directed to AI
  - Conversation lulls (configurable timeout)
- **FR-021:** Generate conversation summaries for new users
- **FR-022:** Distinguish between user-to-user and user-to-AI communication

### 5.5 User Presence
- **FR-023:** Display active user list
- **FR-024:** Show join/leave notifications
- **FR-025:** Update presence status in real-time
- **FR-026:** Display last seen timestamps

---

## 6. Technical Requirements

### 6.1 Frontend Requirements
- **Tech Stack:**
  - React 18+
  - TypeScript 5+
  - WebSocket client (socket.io-client or native)
  - Tailwind CSS or Material-UI for styling
  - React Router for navigation
  - Zustand or Redux for state management

- **Browser Support:**
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+

### 6.2 Backend Requirements
- **Tech Stack:**
  - Python 3.11+
  - FastAPI or Flask with WebSocket support
  - Motor (async MongoDB driver) or PyMongo
  - Pydantic for data validation
  - Google Cloud Client Libraries
  - Redis client for session management

### 6.3 Infrastructure Requirements
- **GCP Services:**
  - Cloud Run for backend hosting
  - MongoDB Atlas on GCP for data persistence
  - Vertex AI for LLM integration
  - Cloud Storage for static assets
  - Cloud CDN for frontend delivery
  - Cloud Load Balancing
  - Identity Platform for authentication
  - Cloud Logging and Monitoring
  - Memorystore (Redis) for session management

### 6.4 Database Schema

**MongoDB Collections:**

```javascript
// conversations collection
{
  _id: ObjectId("..."),
  createdAt: ISODate("2025-08-09T10:00:00Z"),
  lastActivity: ISODate("2025-08-09T15:30:00Z"),
  participants: [
    {
      userId: ObjectId("..."),
      email: "john@example.com",
      name: "John Doe",
      avatarUrl: "https://...",
      joinedAt: ISODate("2025-08-09T10:00:00Z"),
      leftAt: null,
      isActive: true,
      lastSeen: ISODate("2025-08-09T15:30:00Z")
    }
  ],
  messages: [
    {
      _id: ObjectId("..."),
      userId: ObjectId("..."), // null for AI messages
      userName: "John Doe",    // denormalized for performance
      content: "Can you help me write an email response?",
      isAiMessage: false,
      timestamp: ISODate("2025-08-09T10:00:00Z"),
      metadata: {
        edited: false,
        editedAt: null,
        reactions: [],
        attachments: []
      }
    },
    {
      _id: ObjectId("..."),
      userId: null,
      userName: "AI Assistant",
      content: "I'll be happy to help! Please provide the email you need to respond to.",
      isAiMessage: true,
      timestamp: ISODate("2025-08-09T10:00:05Z"),
      metadata: {
        model: "vertex-ai-model",
        tokensUsed: 25
      }
    }
  ],
  metadata: {
    messageCount: 25,
    aiMessageCount: 10,
    participantCount: 2,
    tags: [],
    archived: false
  }
}

// users collection
{
  _id: ObjectId("..."),
  googleId: "1234567890",
  email: "john@example.com",
  name: "John Doe",
  avatarUrl: "https://lh3.googleusercontent.com/...",
  profile: {
    timezone: "America/New_York",
    preferences: {
      notifications: true,
      theme: "light"
    }
  },
  auth: {
    refreshToken: "encrypted_token",
    lastLogin: ISODate("2025-08-09T09:45:00Z")
  },
  stats: {
    totalMessages: 150,
    conversationsJoined: 12,
    firstSeen: ISODate("2025-07-01T10:00:00Z"),
    lastSeen: ISODate("2025-08-09T15:30:00Z")
  },
  createdAt: ISODate("2025-07-01T10:00:00Z"),
  updatedAt: ISODate("2025-08-09T15:30:00Z")
}

// user_sessions collection (for active WebSocket connections)
{
  _id: ObjectId("..."),
  userId: ObjectId("..."),
  conversationId: ObjectId("..."),
  socketId: "socket_xyz123",
  connectionDetails: {
    ipAddress: "192.168.1.1",
    userAgent: "Mozilla/5.0...",
    connectedAt: ISODate("2025-08-09T15:00:00Z")
  },
  status: "active", // active, idle, disconnected
  lastPing: ISODate("2025-08-09T15:30:00Z"),
  expiresAt: ISODate("2025-08-09T23:59:59Z") // TTL index
}

// Indexes for optimal performance:
// - conversations: { "participants.userId": 1, "lastActivity": -1 }
// - conversations: { "messages.timestamp": -1 }
// - users: { "email": 1 } (unique)
// - users: { "googleId": 1 } (unique)
// - user_sessions: { "userId": 1, "status": 1 }
// - user_sessions: { "expiresAt": 1 } (TTL index)
```

### 6.5 MongoDB-Specific Considerations

**Advantages for Chat Application:**
- **Document Model**: Natural fit for conversations with embedded messages
- **Change Streams**: Real-time notifications for WebSocket updates
- **Flexible Schema**: Easy to add new message types and metadata
- **Performance**: Single document read for entire conversation
- **Horizontal Scaling**: Built-in sharding for massive scale

**Implementation Strategies:**
- **Message Pagination**: Use MongoDB's `$slice` operator for efficient message loading
- **Real-time Updates**: Leverage Change Streams for WebSocket notifications
- **Archival**: Move old conversations to separate collection after 30 days
- **Capping**: Consider capped collections for user_sessions with automatic cleanup
- **Aggregation Pipeline**: Use for analytics and reporting features

---

## 7. Non-Functional Requirements

### 7.1 Performance
- **NFR-001:** Page load time < 2 seconds
- **NFR-002:** Message delivery latency < 200ms
- **NFR-003:** Support 100 concurrent users per conversation
- **NFR-004:** AI response time < 3 seconds

### 7.2 Security
- **NFR-005:** All data transmission over HTTPS
- **NFR-006:** WebSocket connections use WSS
- **NFR-007:** Implement rate limiting (100 messages/minute/user)
- **NFR-008:** XSS and CSRF protection
- **NFR-009:** SQL injection prevention
- **NFR-010:** Regular security audits

### 7.3 Reliability
- **NFR-011:** 99.9% uptime SLA
- **NFR-012:** Automated backup every 6 hours with point-in-time recovery
- **NFR-013:** Disaster recovery RTO < 4 hours
- **NFR-014:** Graceful degradation if AI service unavailable
- **NFR-015:** MongoDB replica set with automatic failover
- **NFR-016:** Cross-region replication for disaster recovery

### 7.4 Usability
- **NFR-017:** Mobile-responsive design
- **NFR-018:** WCAG 2.1 AA compliance
- **NFR-019:** Support for keyboard navigation
- **NFR-020:** Clear error messages

---

## 8. Architecture Overview

### 8.1 High-Level Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Cloud CDN  │────▶│  React App  │
└─────────────┘     └─────────────┘     └─────────────┘
        │                                        │
        │ WebSocket                             │
        ▼                                       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cloud     │────▶│   Python    │────▶│  MongoDB    │
│   Load      │     │   Backend   │     │   Atlas     │
│  Balancer   │     │ (Cloud Run) │     │   on GCP    │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                    │
                            │                    │
                            ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Vertex AI  │     │ Memorystore │
                    │     LLM     │     │   (Redis)   │
                    └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  Identity   │
                    │  Platform   │
                    └─────────────┘
```

### 8.2 API Endpoints
- `POST /auth/google` - Google OAuth callback
- `GET /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout user
- `WS /ws` - WebSocket connection for real-time chat
- `GET /api/conversations/:id` - Get conversation with messages
- `GET /api/conversations/:id/messages` - Get paginated messages
- `GET /api/users/me` - Get current user profile
- `POST /api/users/presence` - Update user presence

---

## 9. UI/UX Requirements

### 9.1 Design Principles
- Clean, modern interface with minimal clutter
- High contrast for readability
- Consistent spacing and typography
- Smooth animations and transitions
- Dark mode support

**Branding Elements:**
- Suggested tagline: "Many voices, one conversation"
- Logo concept: Interconnected speech bubbles forming a unified shape
- Color palette: Modern gradients suggesting collaboration and intelligence

### 9.2 Key UI Components
- **Header:** Polylog logo, user profile, logout button
- **User List Panel:** Active users with status indicators
- **Chat Area:** Message history with clear user differentiation
- **Message Input:** Text area with send button and typing indicator
- **Notification Toast:** For user join/leave events

### 9.3 Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

---

## 10. Security and Privacy

### 10.1 Data Protection
- Encrypt data at rest using MongoDB Atlas encryption
- Implement field-level encryption for sensitive data
- Regular security scanning and vulnerability assessment
- Automated backups with point-in-time recovery

### 10.2 Privacy Compliance
- GDPR compliance for EU users
- Clear privacy policy and terms of service
- User data export functionality
- Right to deletion implementation

### 10.3 Access Control
- Role-based access control (future enhancement)
- Session management with timeout
- IP-based rate limiting

---

## 11. Development Phases

### Phase 1: MVP (Weeks 1-6)
- Basic authentication with Google SSO
- Simple chat interface
- WebSocket implementation
- Basic AI integration
- Single conversation support

### Phase 2: Enhanced Features (Weeks 7-10)
- User presence indicators
- Typing indicators
- Message history persistence
- AI context awareness
- Improved UI/UX

### Phase 3: Polish & Scale (Weeks 11-12)
- Performance optimization
- Security hardening
- Monitoring and logging
- Documentation
- Beta testing

---

## 12. Success Metrics

### 12.1 Technical Metrics
- API response time P95 < 500ms
- WebSocket message latency P99 < 300ms
- Zero critical security vulnerabilities
- Code coverage > 80%

### 12.2 User Metrics
- Daily Active Users (DAU)
- Average session duration
- Messages per conversation
- User retention rate
- AI interaction rate

### 12.3 Business Metrics
- Cost per active user
- Infrastructure utilization
- Support ticket volume
- User satisfaction score (NPS)

---

## 13. Risks and Mitigation

### 13.1 Technical Risks
- **Risk:** WebSocket scaling challenges
  - **Mitigation:** Implement connection pooling and horizontal scaling
  
- **Risk:** AI response latency
  - **Mitigation:** Response streaming and caching common queries

### 13.2 Security Risks
- **Risk:** Data breaches
  - **Mitigation:** Regular security audits and penetration testing
  
- **Risk:** DDoS attacks
  - **Mitigation:** Cloud Armor and rate limiting

### 13.3 Business Risks
- **Risk:** High GCP costs
  - **Mitigation:** Usage monitoring and cost optimization strategies

---

## 14. Future Enhancements

### 14.1 Version 2.0 Features
- Multiple conversation rooms
- File sharing capabilities
- Voice and video integration
- AI personality customization
- Advanced moderation tools
- API for third-party integrations

### 14.2 Enterprise Features
- SSO with multiple providers
- Advanced admin dashboard
- Compliance reporting
- Custom AI model training
- On-premise deployment option

---

## 15. Appendices

### 15.1 Glossary
- **LLM:** Large Language Model
- **SSO:** Single Sign-On
- **JWT:** JSON Web Token
- **WebSocket:** Full-duplex communication protocol
- **GCP:** Google Cloud Platform

### 15.2 References
- Google Cloud Documentation
- React Documentation
- WebSocket Protocol RFC 6455
- OAuth 2.0 Specification

### 15.3 Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-08-09 | Product Team | Initial draft |
| 1.1 | 2025-08-09 | Product Team | Updated to MongoDB architecture |
| 1.2 | 2025-08-09 | Product Team | Renamed product to Polylog |

---

**Document Status:** This PRD is a living document and will be updated as requirements evolve during development.