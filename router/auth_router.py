from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

import controller.auth_controller as auth_controller

auth_router = APIRouter()


@auth_router.post('/token')
def create_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> auth_controller.Token:
    return auth_controller.create_token(form_data)


@auth_router.post('/signup', status_code=201)
def signup_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> None:
    if not auth_controller.create_account(form_data):
        raise HTTPException(400)
