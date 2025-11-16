from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    user_email: str

class User(BaseModel):
    id: int
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    model_config = ConfigDict(from_attributes=True)

class UserInDB(User):
    hashed_password: str

class ApiKey(BaseModel):
    key: str
