from pydantic import BaseModel
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
def is_user_friend(my_id: str, friend_id: str) -> bool:
    result = session.users_collection().find_one({
        '_id': ObjectId(my_id),
        'friends': {'$elemMatch': {'user_id': ObjectId(friend_id)}}
    })
    return bool(result)


def is_sent_request(my_id: str, friend_id: str) -> bool:
    result = session.users_collection().find_one({
        '_id': ObjectId(my_id),
        'outgoing_requests.friend_id': {'$elemMatch': {'user_id': ObjectId(friend_id)}} #gemini mówi że zadziała
    })
    return bool(result)


def get_friends(_id: str) -> list[ObjectId]:
    result = session.users_collection().find_one(
        {"_id": ObjectId(_id)},
        {'friends': 1}
    )
    if result is None:
        return []
    return result


def get_incoming_requests(_id: str) -> list[FriendshipRequest]:
    result = session.users_collection().find_one( #czy tu i niżej na pewno jest find_one a nie find_all?
        {'_id': ObjectId(_id)},
        {'incoming_requests': 1}
    )
    if result is None:
        return []
    return result


def get_outgoing_requests(_id: str) -> list[FriendshipRequest]:
    result = session.users_collection().find_one(
        {'_id': ObjectId(_id)},
        {'outgoing_requests': 1}
    )
    if result is None:
        return []
    return result


def send_request(my_id: str, friend_id: str) -> int:
    if is_sent_request(my_id, friend_id):
        return -1

    request_to_friend = FriendshipRequest(friend_id=friend_id)
    request_from_me = FriendshipRequest(friend_id=my_id)

    query = {'_id': my_id}  # add request to my outgoing_requests
    update = {'$addToSet': {'outgoing_requests': {
        'user_id': ObjectId(request_to_friend.user_id),
        'sent_at': request_to_friend.sent_at
    }}}
    matched_count = session.users_collection().update_one(query, update).matched_count

    query = {'_id': friend_id}  # add request to friend's incoming_requests
    update = {'$addToSet': {'incoming_requests': {
        'user_id': ObjectId(request_from_me.user_id),
        'sent_at': request_from_me.sent_at
    }}}
    matched_count += session.users_collection().update_one(query, update)

    return matched_count


def cancel_request(my_id: str, friend_id: str) -> int:

    my_id = ObjectId(my_id)
    friend_id = ObjectId(friend_id)

    query = {'_id': my_id}  # delete request instance for me
    update = {'$pull': {'outgoing_requests': {'user_id': friend_id}}}
    matched_count = session.users_collection().update_one(query, update).matched_count

    query = {'_id': friend_id}  # delete request instance for friend
    update = {'$pull': {'incoming_requests': {'user_id': my_id}}}
    matched_count += session.users_collection().update_one(query, update).matched_count

    return matched_count


def decline_request(my_id: str, friend_id: str) -> int:
    return cancel_request(friend_id, my_id) #operacja odwrota do cancel_request - incoming_request usuwasz u siebie, outgoing_request u friend'a


def approve_request(my_id: str, friend_id: str) -> int:

    matched_count = decline_request(my_id, friend_id)  # remove requests

    my_id = ObjectId(my_id)
    friend_id = ObjectId(friend_id)

    query = {"_id": my_id}  # add friend to my instance
    update = {"$addToSet": {"friends": friend_id}}
    matched_count += session.users_collection().update_one(query, update).matched_count

    query = {"_id": friend_id}  # add me to friend's instance
    update = {"$addToSet": {"friends": my_id}}
    matched_count += session.users_collection().update_one(query, update).matched_count

    return matched_count


def delete_friend(my_id: str, friend_id: str) -> int:

    my_id = ObjectId(my_id)
    friend_id = ObjectId(friend_id)

    query = {"_id": my_id}  # delete friend instance for me
    update = {"$pull": {"friends": friend_id}}
    matched_count = session.users_collection().update_one(query, update).matched_count

    query = {"_id": friend_id}  # delete request instance for friend
    update = {"$pull": {"friends": my_id}}
    matched_count += session.users_collection().update_one(query, update).matched_count

    return matched_count
