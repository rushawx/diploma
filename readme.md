# Student Projects Recommender System

FastAPI backend with Streamlit frontend and PostgreSQL database, featuring intelligent project recommendations using ML transformers.

## Quick Start

```bash
# Start all services
docker compose up --build

# Access services
# Frontend: http://localhost:8501
# Backend: http://localhost:8080
# Backend docs: http://localhost:8080/docs
```

## Features

✅ **JWT Authentication** - Secure user authentication
✅ **CPU-Optimized ML** - Fast inference without GPU requirements
✅ **Project Recommendations** - AI-powered project matching
✅ **Real-time Search** - Instant semantic search using transformers
✅ **User Management** - Complete auth flow with profiles
✅ **Docker-Optimized** - Fast builds and small images

## Development

**Implemented:**
- User authentication and JWT tokens
- Basic recommendation system with ML
- Project search and management UI
- Profile management

**In Progress:**
- Most CRUD endpoints (projects, tags, ratings, etc.)
- Advanced recommendation algorithms
- Complete database schema implementation

## Architecture

```
├── docker-compose.yaml           # Multi-service orchestration
├── recsAppBack/               # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── auth/             # JWT authentication
│   │   ├── db/               # Database layer
│   │   ├── handlers/          # API endpoints
│   │   └── models/            # Data models
│   └── requirements.txt
├── recsAppFront/              # Streamlit frontend
│   ├── app/
│   │   ├── streamlit.py      # Main application
│   │   ├── config.py         # Configuration settings
│   │   └── handlers/          # ML and auth utilities
│   └── requirements.txt
└── .streamlit/secrets.toml    # Streamlit configuration
```

## API Endpoints

**Public:**
- `POST /profile/signup` - Create user account
- `POST /profile/login` - Get JWT token
- `POST /token` - OAuth2 token endpoint
- `GET /` - Service health check

**Protected (JWT required):**
- `GET /about_user` - Get current user
- `GET /profile/me` - Get user profile
- `GET /projects/` - List all projects
- `POST /projects/` - Create new project
- `GET /recommendations/{user_id}` - Get AI recommendations

## Configuration Details

**Backend Config** (`recsAppBack/app/config.py`):
- Database settings and connection pooling
- JWT authentication configuration
- API and security settings
- Server and logging configuration
- ML/embedding settings

**Frontend Config** (`.streamlit/secrets.toml`):
- Backend connection settings
- UI customization options
- ML model and caching configuration
- Performance tuning parameters

## Next Steps

1. Complete CRUD endpoint implementations
2. Add database migrations (Alembic)
3. Implement advanced recommendation algorithms
4. Add comprehensive testing suite
5. Deploy with production-ready configuration