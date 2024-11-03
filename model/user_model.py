from pydantic import BaseModel, Field
from typing import Any
from bson import ObjectId
from db.session import session
from datetime import datetime, timezone
from pydantic import Field


class FriendshipRequest(BaseModel):
    user_id: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PublicUserModel(BaseModel):  # The way anyone can see you
    id: str = Field(alias='_id')
    username: str
    streak: int = 0
    points: int = 0
    friend_count: int = 0


class PrivateUserModel(BaseModel):  # The way your friends see you
    id: str = Field(alias='_id')
    username: str
    streak: int = 0
    points: int = 0
    activities: list[str] = []
    friends: list[str] = []


class UserModel(PrivateUserModel):  # The way only you can see yourself
    incoming_requests: list[FriendshipRequest] = []
    outgoing_requests: list[FriendshipRequest] = []


class NewUserModel(BaseModel):  # Used for new user creation, maybe unnecessary?...
    username: str
    password_hash: str


# Functions related to the user itself
def get_user_by_id(_id: str) -> UserModel | None:
    result: dict[str, Any] | None = session.users_collection().find_one({'_id': ObjectId(_id)})

    if result is None:
        return None
    result['_id'] = str(result['_id'])
    return UserModel(**result)


def get_user_id_by_username(username: str) -> str | None:
    result = session.users_collection().find_one({'username': username})

    if result is None:
        return None
    return str(result['_id'])


def get_user_password_by_username(username: str) -> str | None:
    result = session.users_collection().find_one({'username': username})

    if result is None:
        return None
    return result['password_hash']


def create_user(user: NewUserModel) -> bool:
    try:
        inserted_id = session.users_collection().insert_one(user.model_dump()).inserted_id
    except Exception as e:
        print(e)
        return False

    return bool(inserted_id)


def get_public_user(user_id: str) -> PublicUserModel:
    result = session.users_collection().find_one({'_id': ObjectId(user_id)})
    result['_id'] = user_id
    friend_count = len(result['friends']) if 'friends' in result.keys() else 0
    result['friend_count'] = friend_count
    return PublicUserModel(**result)


def get_private_user(user_id: str) -> PrivateUserModel:
    result = session.users_collection().find_one({'_id': ObjectId(user_id)})
    result['_id'] = user_id
    return PrivateUserModel(**result)


# Functions related to friendship
def is_user_friend(user1_id: str, user2_id: str) -> bool:
    result = session.users_collection().find_one({
        '_id': ObjectId(user1_id),
        'friends': {'$elemMatch': {'user_id': ObjectId(user2_id)}}
    })
    return bool(result)
