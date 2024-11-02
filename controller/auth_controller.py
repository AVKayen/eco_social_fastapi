from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from typing import Annotated
import os
from datetime import datetime, timedelta, timezone

from model.user_model import get_user_password_by_username, get_user_id_by_username


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    username: str


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
TOKEN_SECRET = os.getenv('TOKEN_SECRET')
if not TOKEN_SECRET:
    raise Exception('No token secret specified in the env variables.')


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    password_hash = get_user_password_by_username(username)
    if not password_hash:
        return False
    if not verify_password(password, password_hash):
        return False
    return True


def create_access_token(payload: dict, expires_delta: timedelta | None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def parse_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception

    token_data = TokenData(user_id=payload['sub'], username=payload['username'])
    return token_data


def create_token(form_data: OAuth2PasswordRequestForm) -> Token:
    authenticated: bool = authenticate_user(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = get_user_id_by_username(form_data.username)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        payload={'sub': user_id, 'username': form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")