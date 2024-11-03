from typing import Annotated

from fastapi import Depends, APIRouter

from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model


user_router = APIRouter()


@user_router.get('/me')
def me(token_data: Annotated[TokenData, Depends(parse_token)]) -> user_model.UserModel:
    return user_model.get_user_by_id(token_data.user_id)


@user_router.get('/{user_id}')
def get_user(
        user_id: str, token_data: Annotated[TokenData, Depends(parse_token)]
) -> user_model.PublicUserModel | user_model.PrivateUserModel:

    if user_model.is_user_friend(token_data.user_id, user_id):
        return user_model.get_private_user(user_id)
    return user_model.get_public_user(user_id)
