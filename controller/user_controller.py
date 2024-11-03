from controller.auth_controller import TokenData
from model.user_model import UserModel, get_user_by_id


def get_my_profile(token_data: TokenData) -> UserModel | None:
    return get_user_by_id(token_data.user_id)
