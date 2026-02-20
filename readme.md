# Student Projects Recommender System

A recommendation system for student projects built with FastAPI and PostgreSQL. This system helps students discover relevant projects based on their interests, interactions, and ratings.

## Features

- **User Management**: User registration, authentication, and profile management
- **Project Management**: Create, read, update, and delete student projects
- **Ratings System**: Users can rate projects
- **Interactions Tracking**: Track user interactions with projects
- **Tagging System**: Organize projects with tags
- **Recommendations Engine**: Get personalized project recommendations
- **JWT Authentication**: Secure API endpoints with JWT tokens

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (PyJWT)
- **Containerization**: Docker & Docker Compose
- **Python Version**: 3.x

## Project Structure

```
.
├── docker-compose.yaml          # Docker orchestration
├── readme.md                    # Project documentation
├── recsApp/                     # Main application
│   ├── Dockerfile               # Container configuration
│   ├── requirements.txt         # Python dependencies
│   └── app/
│       ├── main.py              # Application entry point
│       ├── auth/                # Authentication logic
│       │   └── auth.py
│       ├── db/                  # Database configuration
│       │   └── engine.py
│       ├── handlers/            # API endpoints
│       │   ├── interactions.py  # Interaction tracking
│       │   ├── projects.py      # Project CRUD
│       │   ├── ratings.py       # Rating system
│       │   ├── recommendations.py  # Recommendation engine
│       │   ├── tags.py          # Tag management
│       │   └── users.py         # User management
│       ├── ml/                  # Machine learning models
│       ├── models/              # Database models
│       │   └── users.py
│       └── utils/               # Utility functions
│           └── utils.py
└── supplementary/
    └── ddl.sql                  # Database schema
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- `.env` file with the following variables:
  ```
  PG_USER=your_postgres_user
  PG_PASSWORD=your_postgres_password
  PG_DATABASE=your_database_name
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd diploma
   ```

2. Create a `.env` file in the root directory with your PostgreSQL credentials.

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:80`

### Development Setup

To run the application locally without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r recsApp/requirements.txt
   ```

3. Set up your database connection and environment variables.

4. Run the application:
   ```bash
   cd recsApp
   uvicorn app.main:app --reload --host 0.0.0.0 --port 80
   ```

## API Documentation

Once the application is running, you can access:

- **Interactive API documentation (Swagger UI)**: `http://localhost/docs`
- **Alternative API documentation (ReDoc)**: `http://localhost/redoc`

### Main Endpoints

- `GET /` - Welcome message
- `POST /token` - Obtain JWT access token
- `GET /about_user` - Get current user information (requires authentication)

### API Endpoints

#### Users (`/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/` | Get all users |
| `GET` | `/users/{user_id}` | Get a specific user by ID |
| `POST` | `/users/` | Create a new user |
| `PUT` | `/users/{user_id}` | Update an existing user |
| `DELETE` | `/users/{user_id}` | Delete a user |

#### Projects (`/projects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/` | Get all projects |
| `GET` | `/projects/{user_id}` | Get all projects for a specific user |
| `GET` | `/projects/{project_id}` | Get a specific project by ID |
| `POST` | `/projects/` | Create a new project |
| `PUT` | `/projects/{project_id}` | Update an existing project |
| `DELETE` | `/projects/{project_id}` | Delete a project |

#### Ratings (`/ratings`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ratings/` | Get all ratings |
| `GET` | `/ratings/{user_id}` | Get all ratings by a specific user |
| `GET` | `/ratings/{rating_id}` | Get a specific rating by ID |
| `POST` | `/ratings/` | Create a new rating |
| `PUT` | `/ratings/{rating_id}` | Update an existing rating |
| `DELETE` | `/ratings/{rating_id}` | Delete a rating |

#### Interactions (`/interactions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/interactions/` | Get all interactions |
| `GET` | `/interactions/{user_id}` | Get all interactions by a specific user |
| `GET` | `/interactions/{interaction_id}` | Get a specific interaction by ID |
| `POST` | `/interactions/` | Create a new interaction |
| `PUT` | `/interactions/{interaction_id}` | Update an existing interaction |
| `DELETE` | `/interactions/{interaction_id}` | Delete an interaction |

#### Tags (`/tags`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tags/` | Get all tags |
| `GET` | `/tags/{user_id}` | Get all tags for a specific user |
| `GET` | `/tags/{tag_id}` | Get a specific tag by ID |
| `POST` | `/tags/` | Create a new tag |
| `PUT` | `/tags/{tag_id}` | Update an existing tag |
| `DELETE` | `/tags/{tag_id}` | Delete a tag |

#### Recommendations (`/recommendations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/recommendations/{user_id}` | Get personalized project recommendations for a user |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Obtain a token by sending a POST request to `/token` with your credentials:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. Include the token in the Authorization header of subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

## Database

The application uses PostgreSQL as its database. The database schema is defined in `supplementary/ddl.sql`. 

The database container includes a health check and will automatically initialize with the schema from the `init/pg` directory if configured.

## Contributing

This is a diploma project. Feel free to fork and adapt for your own needs.
