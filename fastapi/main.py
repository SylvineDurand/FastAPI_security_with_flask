from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import os
from dotenv import load_dotenv

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.schemas import *
from src.database import get_db, UserDB

import logging

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

SECRET_KEY = os.getenv("FASTAPI_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# functions for user authentication
# ---------------------------------------------------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to check if the user is authentified via verification of the token from the request header.
# it user is correctly identified, returns the uset, else raises an exception.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



 # function for user management 
 # ---------------------------------------------------------------------
def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = UserDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        user_role=user.user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


 # Endpoints
 # ---------------------------------------------------------------------

 # Authentication and user management 

 # generation of a token upon log in (route login in flask app)
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# returns current user
@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

# creation of a new user
@app.post("/create_user/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    logging.info(f"object db_user is : {db_user}")
    if db_user:
        logging.debug(f"Username {user.username} already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)


# get list of all users
@app.get("/users_list/", response_model=list[User])
def read_users(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your role is {current_user.user_role}, you must be an admin to access this page",
        )
    return db.query(UserDB).all()


# accessible only to admins
@app.get("/admin_only", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your role is {current_user.user_role}, you must be an admin to access this page",
        )
    return current_user

# accessible only to admins and ai team
@app.get("/admin_and_ai_only", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):

    if current_user.user_role not in ["admin", "ai_team"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your role is {current_user.user_role}, you must be an admin or belong to ai team to access this page",
        )
    return current_user
