from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from controller.auth_controller import Token, create_token, get_password_hash

auth_router = APIRouter()


@auth_router.post('/token')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return create_token(form_data)

@auth_router.get('/hash_password')
def hash_password(password: str) -> str:
    return get_password_hash(password)
