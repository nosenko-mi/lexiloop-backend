from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import jwt
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.auth import User as UserModel
from app.db.models import APIKey, User as UserData
from app.service.auth.auth_handler import get_user_by_email, get_user_by_id
from app.service.auth.config import JWT_ALGORITHM, JWT_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
    ) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_user_by_email(db, email)  # type: ignore
    if user is None:
        raise credentials_exception
    return UserModel(id = user.id, email=user.email, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active) # type: ignore

async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_api_key_from_header(request: Request) -> str:
    api_key = request.headers.get("Authorization")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    # Assuming the API key is sent as "Bearer <API_KEY>"
    api_key = api_key.split(" ")[1] if api_key.startswith("Bearer ") else api_key
    return api_key


async def get_user_by_api_key(api_key: str, db: Session = Depends(get_db)) -> UserModel:
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    user = get_user_by_id(db, db_api_key.user_id) # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for the provided API key",
        )
    return UserModel(id = user.id, email=user.email, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active) # type: ignore


async def get_current_user_or_api_key(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    api_key: str = Depends(get_api_key_from_header)
) -> UserModel | str:
    if api_key:
        return await get_user_by_api_key(api_key, db)
    
    elif token:
        user = await get_current_user(token, db)
        return user
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neither user nor api key were provided",
        )