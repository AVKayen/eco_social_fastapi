from auth_controller import TokenData
from model.user_model import get_user_by_id


class UserController:
    @staticmethod
    def me(token_data: TokenData):
        user = get_user_by_id(token_data.user_id)
        return user
