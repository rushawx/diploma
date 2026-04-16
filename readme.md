# Student Projects Recommender System

Diploma project with:

- FastAPI backend
- Streamlit frontend
- PostgreSQL database

## Current Status

The project is in active development.

- Auth/profile flow is implemented (`/profile/signup`, `/profile/login`, `/token`, `/about_user`)
- Most CRUD-like routes in `app/handlers/*` are currently stubs (`NotImplementedError`)
- Frontend already supports signup/login and a basic transformer-based project search UI

## Repository Structure

```text
.
├── docker-compose.yaml
├── readme.md
├── init/
│   └── pg/                    # Optional DB init scripts mounted into Postgres
├── recsAppBack/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── auth/
│       ├── db/
│       ├── handlers/
│       ├── models/
│       └── utils/
├── recsAppFront/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── streamlit.py
│       ├── handlers/
│       └── resources/
└── supplementary/
    └── ddl.sql               # Target SQL schema
```

## Requirements

- Docker
- Docker Compose plugin (`docker compose`)

## Environment Variables

Create `.env` in the repository root:

```env
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=recs
PG_HOST=db
PG_PORT=5432

SECRET_KEY=change-me
ADMIN_PASSWORD=change-me
```

## Run With Docker

```bash
docker compose up --build
```

Services:

- Frontend (Streamlit): http://localhost:8501
- Backend (FastAPI): http://localhost:8080
- Backend docs (Swagger): http://localhost:8080/docs
- PostgreSQL: localhost:5432

## Local Run (Without Docker)

### Backend

```bash
cd recsAppBack
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend

```bash
cd recsAppFront
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit.py
```

Note: when running frontend locally, `BASE_URL` in `recsAppFront/app/streamlit.py` may need adjustment (it is currently set for Docker networking: `back:8080`).

## Implemented API Endpoints

- `GET /` - service health/welcome message
- `POST /token` - issue JWT token (OAuth2 password form)
- `GET /about_user` - get current user from token
- `POST /profile/signup` - create user
- `POST /profile/login` - login and receive JWT token

## Database Notes

- Docker Postgres mounts `./init/pg` into `/docker-entrypoint-initdb.d`
- Right now `init/pg` is empty, so no SQL bootstrap runs automatically
- Target schema is available in `supplementary/ddl.sql`

## Next Development Steps

- Implement handlers in `recsAppBack/app/handlers/*`
- Align SQLAlchemy models with `supplementary/ddl.sql`
- Add migrations (e.g., Alembic)
- Add tests for auth/profile and recommendation flow
