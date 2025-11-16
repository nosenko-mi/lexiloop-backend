import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import schemas
from app.db import user_settings_crud
from app.db.dependencies import get_db
from app.models.auth import User as UserModel
from app.models.user_settings import UserSettingsDTO
from app.service.auth.dependencies import get_current_user_or_api_key

router = APIRouter(
    prefix="/api/settings",
    tags=["settings"],
    dependencies=[Depends(get_current_user_or_api_key)] 
)

logger = logging.getLogger(__name__)

@router.get(
    "/", 
    response_model=UserSettingsDTO,
    summary="Get current user's settings"
)
def read_user_settings(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user_or_api_key)
):
    """
    Fetches the native and target language settings for the
    currently authenticated user.
    
    Returns 404 if no settings have been set yet (e.g., new user).
    """
    logger.info(f"Fetching settings for user_id: {current_user.id}")
    settings = user_settings_crud.get_user_settings(db, user_id=current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User settings not found. Please create them first."
        )
    

    return UserSettingsDTO(user_id=settings.user_id, user_email=settings.user_email, native_language_code=settings.native_language_code, target_language_code=settings.target_language_code)

@router.post(
    "/", 
    response_model=UserSettingsDTO,
    summary="Create or update user's settings"
)
def create_or_update_settings(
    settings: schemas.UserSettingsCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user_or_api_key)
):
    """
    Creates or updates the native and target language settings
    for the currently authenticated user.
    """
    logger.info(f"Updating settings for user_id: {current_user.id}")
    settings = user_settings_crud.create_or_update_user_settings(
        db, 
        user_id=current_user.id, 
        settings=settings
    )

    return UserSettingsDTO(user_id=settings.user_id, user_email=settings.user_email, native_language_code=settings.native_language_code, target_language_code=settings.target_language_code)
