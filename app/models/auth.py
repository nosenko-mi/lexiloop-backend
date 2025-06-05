from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_email: int

class User(BaseModel):
    id: int
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None

class UserInDB(User):
    hashed_password: str

class ApiKey(BaseModel):
    key: str
