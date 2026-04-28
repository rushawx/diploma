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

<li>✅ <b>JWT Authentication</b> - Secure user authentication with profile management
<li>✅ <b>Project Management</b> - Full CRUD operations with embedding generation
<li>✅ <b>AI-Powered Search</b> - Semantic search using transformer models + Tags based search using cosine similarity
<li>✅ <b>User Projects</b> - Claim and manage personal projects
<li>✅ <b>PostgreSQL + pgvector</b> - Optimized vector database for embeddings
<li>✅ <b>Docker-Optimized</b> - Fast builds and small images

## Development

**Implemented:**
- Complete user authentication flow
- Project CRUD operations with automatic embedding and tags generation
- Semantic project search and recommendations
- User profile and project claiming functionality
- Database initialization with project embeddings

## Architecture

```
├── docker-compose.yaml           # Multi-service orchestration
├── recsAppBack/               # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── auth/             # JWT authentication
│   │   ├── db/               # Database layer with pgvector
│   │   ├── handlers/          # API endpoints
│   │   └── models/            # Data models
│   └── requirements.txt
├── recsAppFront/              # Streamlit frontend
│   ├── app/
│   │   ├── streamlit.py      # Main application
│   │   ├── config.py         # Configuration settings
│   │   └── handlers/          # ML and auth utilities
│   └── requirements.txt
└── recsAppInit/               # Data initialization service
    ├── app/
    │   ├── main.py          # Embedding generation
    │   ├── config.py         # Configuration settings
    │   └── models.py         # Data models
    └── requirements.txt
```

## API Endpoints

**Public:**
- `POST /profile/signup` - Create user account
- `POST /profile/login` - Get JWT token
- `GET /` - Service health check

**Protected (JWT required):**
- `GET /projects/` - List all projects (simplified view)
- `GET /projects/with-embeddings` - List projects with embeddings
- `GET /projects/user/{user_id}` - Get projects by user
- `GET /projects/{project_id}` - Get specific project details
- `POST /projects/` - Create new project (auto-generates embeddings)
- `PUT /projects/{project_id}` - Update project (claim ownership)
- `DELETE /projects/{project_id}` - Soft delete project
- `GET /profile/me` - Get user profile

## Configuration Details

**Backend Config** (`recsAppBack/app/config.py`):
- Database settings and connection pooling
- JWT authentication configuration
- API and security settings
- ML/embedding model configuration

**Frontend Config** (`.streamlit/secrets.toml`):
- Backend connection settings
- UI customization options
- ML model and caching configuration
- Performance tuning parameters

**Init Service** (`recsAppInit/app/config.py`):
- Database connection settings
- Data file paths
- Embedding model configuration
- Batch processing settings
