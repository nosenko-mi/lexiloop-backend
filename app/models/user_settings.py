from pydantic import BaseModel, EmailStr, ConfigDict


class UserSettingsDTO(BaseModel):
    user_id: int
    user_email: EmailStr
    native_language_code: str
    target_language_code: str

    class ConfigDict:
        from_attributes = True
