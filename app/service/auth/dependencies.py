from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer # Use only this header scheme
from typing import Annotated
import jwt
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.auth import TokenData, User as UserModel
from app.db.models import APIKey, User as UserData
from app.service.auth.auth_handler import get_user_by_email, get_user_by_id
from app.service.auth.config import JWT_ALGORITHM, JWT_SECRET

authorization_header_scheme = APIKeyHeader(name="Authorization", auto_error=False)
refresh_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token/refresh")

async def get_current_user(token: str, db: Session) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate JWT credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
        
    # Convert DB model to Pydantic model
    return UserModel.model_validate(user)

# --- API Key Validation Helper (remains mostly the same) ---
async def get_user_by_api_key(api_key: str, db: Session) -> UserModel:
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
        
    user = get_user_by_id(db, db_api_key.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User associated with API key not found",
        )
        
    return UserModel.model_validate(user)

async def get_current_user_or_api_key(
    auth_header_value: str | None = Depends(authorization_header_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Authenticates a user based on the Authorization header.
    It tries to validate as a Bearer token first, then as a plain API key.
    """
    
    unauthorized_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth_header_value:
        raise unauthorized_exception

    parts = auth_header_value.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        try:
            user = await get_current_user(token=token, db=db)
            if not user.is_active:
                 raise HTTPException(status_code=400, detail="Inactive user")
            return user
        except HTTPException as jwt_exc:
             if jwt_exc.status_code == status.HTTP_401_UNAUTHORIZED and \
                jwt_exc.detail == "Could not validate JWT credentials":
                 pass
             else:
                 raise jwt_exc
    
    key_to_check = token if 'token' in locals() else auth_header_value 
    
    try:
        user = await get_user_by_api_key(api_key=key_to_check, db=db)
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user associated with API key")
        return user
    except HTTPException as api_key_exc:
         if api_key_exc.status_code == status.HTTP_401_UNAUTHORIZED:
             raise unauthorized_exception
         else: 
             raise api_key_exc 
         
async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user_or_api_key)],
) -> UserModel:
    return current_user


async def get_current_user_from_refresh_token(
    token: str = Depends(refresh_oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "refresh":
            raise credentials_exception
            
        token_data = TokenData(user_email=email)
    except jwt.PyJWTError:
        raise credentials_exception
        
    return token_data.user_email