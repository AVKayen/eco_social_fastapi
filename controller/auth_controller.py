from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from typing import Annotated, Dict, Any
from datetime import datetime, timedelta, timezone

from model.user_model import get_user_password_by_username, get_user_id_by_username, create_user

from config.settings import settings


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    username: str


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    password_hash = get_user_password_by_username(username)
    if not password_hash:
        return False
    if not verify_password(password, password_hash):
        return False
    return True


def create_access_token(payload: Dict[str, Any], expires_delta: timedelta | None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.token_secret, algorithm=ALGORITHM)
    return encoded_jwt


def parse_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.token_secret, algorithms=[ALGORITHM])
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

    user_id: str | None = get_user_id_by_username(form_data.username)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. This can only happen if the user was deleted while they were logged in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        payload={'sub': user_id, 'username': form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


def create_account(form_data: OAuth2PasswordRequestForm) -> bool:
    if get_user_id_by_username(form_data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username taken')
    password_hash = get_password_hash(form_data.password)
    return create_user(username=form_data.username, password_hash=password_hash)

