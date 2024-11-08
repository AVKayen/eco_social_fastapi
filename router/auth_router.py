from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from controller.auth_controller import Token, create_token, signup_user

auth_router = APIRouter()


@auth_router.post('/token')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return create_token(form_data)


@auth_router.post('/signup', status_code=201)
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> None:
    if not signup_user(form_data):
        raise HTTPException(400)
