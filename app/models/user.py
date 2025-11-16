from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserDTO(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str

    class ConfigDict:
        from_attributes = True
