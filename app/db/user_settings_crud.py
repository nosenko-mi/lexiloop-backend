from sqlalchemy.orm import Session, joinedload
from app.db.models import UserSettings
from app.db.schemas import UserSettingsCreate


def get_user_settings(db: Session, user_id: int) -> UserSettings | None:
    """Fetches settings for a specific user, eagerly loading the owner."""
    return db.query(UserSettings)\
        .options(joinedload(UserSettings.owner))\
        .filter(UserSettings.user_id == user_id)\
        .first()

def create_or_update_user_settings(
    db: Session, 
    user_id: int, 
    settings: UserSettingsCreate
) -> UserSettings:
    """
    Updates existing settings or creates new ones for a user (Upsert).
    """
    
    db_settings = get_user_settings(db, user_id)
    
    if db_settings:
        db_settings.native_language_code = settings.native_language_code
        db_settings.target_language_code = settings.target_language_code
    else:
        db_settings = UserSettings(
            **settings.model_dump(), 
            user_id=user_id
        )
        db.add(db_settings)
    
    db.commit()
    db.refresh(db_settings)
    db.refresh(db_settings.owner)
    return db_settings