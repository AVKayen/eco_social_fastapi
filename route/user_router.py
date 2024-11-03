from typing import Annotated

from fastapi import Depends, APIRouter

from controller.auth_controller import TokenData, parse_token
from model.user_model import UserModel, get_user_by_id


user_router = APIRouter()


@user_router.get('/me')
def me(token_data: Annotated[TokenData, Depends(parse_token)]) -> UserModel:
    return get_user_by_id(token_data.user_id)
