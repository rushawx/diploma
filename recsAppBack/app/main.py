import logging
from typing import Annotated

import uvicorn
from app.config import settings
from app.auth.auth import create_jwt_token, get_current_active_user, get_user_from_db
from app.db.engine import Base, engine
from app.handlers.profile import router as profile_router
from app.handlers.projects import router as projects_router
from app.handlers.tags import router as tags_router
from app.handlers.users import router as users_router
from app.models.users import User
from app.utils.utils import init_superuser
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"Response: {response.status_code}")

    return response


app.include_router(projects_router)
app.include_router(tags_router)
app.include_router(users_router)
app.include_router(profile_router)

Base.metadata.create_all(bind=engine)

init_superuser()


@app.get("/")
async def root():
    return {
        "message": f"This is {settings.PROJECT_NAME} v{settings.VERSION}",
        "debug": settings.DEBUG,
    }


@app.post("/token")
async def token(user: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user_from_db = get_user_from_db(user.username)
    if not user_from_db or user_from_db.password != user.password:
        logger.warning(f"Failed login attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User logged in successfully: {user.username}")
    return {
        "access_token": create_jwt_token({"sub": user_from_db.nick_name}),
        "token_type": "bearer",
    }


@app.get("/about_user")
async def about_user(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    return {"message": f"This is a user: {current_user.nick_name}"}


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
