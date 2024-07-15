from pydantic import BaseModel
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    user_role: str


class UserInDB(User):
    hashed_password: str

# for user creation
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    user_role: str 