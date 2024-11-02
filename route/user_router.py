from typing import Annotated

from fastapi import Depends, APIRouter

from controller.user_controller import UserController
from controller.auth_controller import TokenData, parse_token


user_router = APIRouter()


@user_router.get('/me')
def me(token_data: Annotated[TokenData, Depends(parse_token)]):
    return UserController.me(token_data)
