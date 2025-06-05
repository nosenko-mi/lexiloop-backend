from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.db.models import User
from app.models.user import UserCreate, UserOut
from app.models.auth import ApiKey, Token
from app.service.auth.auth_handler import authenticate_user, create_access_token, create_user, generate_api_key
from app.service.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.service.auth.dependencies import get_current_active_user


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/key", response_model=ApiKey)
def create_api_key(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return generate_api_key(db, user_id=current_user.id)


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(email=user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_in)
