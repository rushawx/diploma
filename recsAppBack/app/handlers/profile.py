import uuid

from app.auth.auth import create_jwt_token, get_current_active_user, get_user_from_db
from app.db.engine import User
from app.models.profile import UserLogin, UserSignup
from app.utils.utils import get_db
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/signup")
async def signup(input: UserSignup, db=Depends(get_db)):
    user = User(
        id=str(uuid.uuid4()),
        nick_name=input.nick_name,
        password=input.password,
        first_name=input.first_name,
        middle_name=input.middle_name,
        last_name=input.last_name,
        email_address=input.email_address,
        phone_number=input.phone_number,
        self_bio=input.self_bio,
        user_type=input.user_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"Message": f"User {user.nick_name} created"}


@router.post("/login")
async def login(input: UserLogin, db=Depends(get_db)):
    user_from_db = get_user_from_db(input.nick_name)
    if not user_from_db or user_from_db.password != input.password:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "access_token": create_jwt_token({"sub": user_from_db.nick_name}),
        "token_type": "bearer",
    }


@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return {
        "id": str(current_user.id),
        "nick_name": current_user.nick_name,
        "first_name": current_user.first_name,
        "middle_name": current_user.middle_name,
        "last_name": current_user.last_name,
        "email_address": current_user.email_address,
        "phone_number": current_user.phone_number,
        "self_bio": current_user.self_bio,
        "user_type": current_user.user_type,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }
