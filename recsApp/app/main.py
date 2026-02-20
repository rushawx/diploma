from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth import create_jwt_token, decode_jwt_token, get_user_from_db
from app.db.engine import Base, engine
from app.handlers.interactions import router as interactions_router
from app.handlers.projects import router as projects_router
from app.handlers.ratings import router as ratings_router
from app.handlers.recommendations import router as recommendations_router
from app.handlers.tags import router as tags_router
from app.handlers.users import router as users_router
from app.models.users import User
from app.utils.utils import init_superuser

app = FastAPI()

app.include_router(interactions_router)
app.include_router(projects_router)
app.include_router(ratings_router)
app.include_router(recommendations_router)
app.include_router(tags_router)
app.include_router(users_router)

Base.metadata.create_all(bind=engine)

init_superuser()


@app.get("/")
async def root():
    return {"message": "This is a Student Projects Recommender System"}


@app.post("/token")
async def token(user: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user_from_db = get_user_from_db(user.username)
    if not user_from_db or user_from_db.password != user.password:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "access_token": create_jwt_token({"sub": user_from_db.nick_name}),
        "token_type": "bearer",
    }


@app.get("/about_user")
async def about_user(user: User = Depends(decode_jwt_token)) -> dict:
    user_from_db = get_user_from_db(user["sub"])
    return {"message": f"This is a user: {user_from_db.nick_name}"}


if __name__ == "__main__":
    uvicorn.run(app)
