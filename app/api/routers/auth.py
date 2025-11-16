from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.db.models import User
from app.models.user import UserCreate, UserDTO
from app.models.auth import ApiKey, Token
from app.service.auth.auth_handler import authenticate_user, create_access_token, create_refresh_token, create_user, generate_api_key
from app.service.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.service.auth.dependencies import get_current_active_user, get_current_user_from_refresh_token


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
        
    # Create Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "type": "access"},
        expires_delta=access_token_expires
    )
    
    # Create Refresh Token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return Token(
        access_token=access_token, 
        token_type="bearer", 
        refresh_token=refresh_token  # Return the new token
    )


@router.post("/key", response_model=ApiKey)
def create_api_key(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return generate_api_key(db, user_id=current_user.id)


@router.post("/register", response_model=UserDTO)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(email=user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_in)


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    current_user_email: str = Depends(get_current_user_from_refresh_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email, "type": "access"}, 
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return Token(
        access_token=new_access_token, 
        token_type="bearer", 
        refresh_token=new_refresh_token
    )
