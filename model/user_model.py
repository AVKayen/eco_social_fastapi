from pymongo.mongo_client import Any
from typing_extensions import Dict
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from db.session import session

from datetime import UTC, datetime


class FriendshipRequest(BaseModel):
    user_id: str
    sent_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class UserModel(BaseModel):
    id: str = Field(alias='_id')
    username: str
    streak: int = 0
    points: int = 0
    activities: list[str] = []
    friends: list[str] = []
    incoming_requests: list[FriendshipRequest] = []
    outgoing_requests: list[FriendshipRequest] = []


class NewUserModel(BaseModel):
    username: str
    password_hash: str


def get_user_by_id(_id: str) -> UserModel | None:
    result: Dict[str, Any] | None = session.users_collection().find_one({'_id': ObjectId(_id)})

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


def create_user(user: NewUserModel) -> str | None:
    try:
        inserted_id = session.users_collection().insert_one(dict(user)).inserted_id
    except Exception as e:
        print(e)
        return None


    return inserted_id
