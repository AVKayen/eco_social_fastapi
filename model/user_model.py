from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from db.session import session

from datetime import datetime


class FriendshipRequest(BaseModel):
    user_id: str
    send_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UserModel(BaseModel):
    id: str = Field(..., alias='_id')
    username: str
    streak: Optional[int] = 0
    points: Optional[int] = 0
    activities: Optional[list[str]] = []
    friends: Optional[list[str]] = []
    incoming_requests: Optional[list[FriendshipRequest]] = []
    outgoing_requests: Optional[list[FriendshipRequest]] = []


class NewUserModel(BaseModel):
    username: str
    password_hash: str


def get_user_by_id(_id: str):
    result = session.users_collection().find_one({'_id': ObjectId(_id)})
    result['_id'] = str(result['_id'])
    return UserModel(**result)


def get_user_password_by_username(username: str):
    result = session.users_collection().find_one({'username': username})
    return result['password_hash']


def create_user(user: NewUserModel):
    inserted_id = session.users_collection().insert_one(dict(user)).inserted_id
    return inserted_id
