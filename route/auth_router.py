from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from controller.auth_controller import Token, create_token, signup_user

auth_router = APIRouter()


@auth_router.post('/token')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return create_token(form_data)


@auth_router.post('/signup')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> bool:
    return signup_user(form_data)
