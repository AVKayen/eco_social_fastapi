from typing import Annotated

from fastapi import Depends, APIRouter

import controller.user_controller as user_controller
from controller.auth_controller import TokenData, parse_token
from model.user_model import UserModel


user_router = APIRouter()


@user_router.get('/me')
def me(token_data: Annotated[TokenData, Depends(parse_token)]) -> UserModel:
    return user_controller.get_my_profile(token_data)
