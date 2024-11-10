import heapq

from pydantic import BaseModel, ConfigDict
from typing import Any, Annotated
from bson import ObjectId

from db.session import session
from datetime import datetime, timezone
from pydantic import Field

from model.object_id_model import ObjectIdPydanticAnnotation


class FriendCloseness:
    def __init__(self, _id: str):
        self._id = _id
        self.count = 0

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if self.id == other.id:
            self.count += 1
            return True
        return False

    def __lt__(self, other):
        return self.count < other.count

    @property
    def id(self):
        return self._id


class FriendshipRequest(BaseModel):
    user_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseUserModel(BaseModel):
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation] = Field(alias='_id')
    username: str
    streak: int = 0
    points: int = 0
    profile_pic: str = ''
    about_me: str = ''

    model_config = ConfigDict(populate_by_name=True)


class PublicUserModel(BaseUserModel):  # The way anyone can see you
    friend_count: int = 0


class PrivateUserModel(BaseUserModel):  # The way your friends see you
    activities: list[str] = []
    friends: list[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = []


class UserModel(PrivateUserModel):  # The way only you can see yourself
    incoming_requests: list[FriendshipRequest] = []
    outgoing_requests: list[FriendshipRequest] = []
    last_time_on_streak: datetime | None = None


# Functions related to the user itself
def get_user_by_id(user_id: str) -> UserModel | None:
    result: dict[str, Any] | None = session.users_collection().find_one({'_id': ObjectId(user_id)})

    if result is None:
        return None

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


def create_user(username: str, password_hash: str) -> bool:

    inserted_id = session.users_collection().insert_one({
        'username': username,
        'password_hash': password_hash
    }).inserted_id

    return bool(inserted_id)


def get_public_user(user_id: str) -> PublicUserModel | None:
    result = session.users_collection().find_one({'_id': ObjectId(user_id)})
    if not result:
        return None
    friend_count = len(result['friends']) if 'friends' in result.keys() else 0
    result['friend_count'] = friend_count
    return PublicUserModel(**result)


def get_private_user(user_id: str) -> PrivateUserModel | None:
    result = session.users_collection().find_one({'_id': ObjectId(user_id)})
    if not result:
        return None
    return PrivateUserModel(**result)


def update_after_activity_creation(
        user_id: str, new_points: int, new_streak: int, new_last_time_on_streak: datetime
) -> bool:
    modified_count = session.users_collection().update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'streak': new_streak,
            'last_time_on_streak': new_last_time_on_streak,
            'points': new_points
        }}
    ).modified_count
    return modified_count == 1


# Functions related to friendship
def is_user_friend(my_id: str, friend_id: str) -> bool:
    result = session.users_collection().find_one({
        '_id': ObjectId(my_id),
        'friends': ObjectId(friend_id)
    })
    print(result)
    return bool(result)


def is_request_outgoing(my_id: str, friend_id: str) -> bool:
    result = session.users_collection().find_one({
        '_id': ObjectId(my_id),
        'outgoing_requests': {'$elemMatch': {'user_id': ObjectId(friend_id)}}
    })

    return bool(result)


def is_request_incoming(my_id: str, friend_id: str) -> bool:
    return is_request_outgoing(friend_id, my_id)


def get_friends(_id: str) -> list[ObjectId]:
    result = session.users_collection().find_one(
        {'_id': ObjectId(_id)},
        {'_id': 0, 'friends': 1}
    )
    if result is None:
        return []
    friends = result['friends'] if 'friends' in result else []
    return friends


def get_incoming_requests(_id: str) -> list[FriendshipRequest]:
    result = session.users_collection().find_one(  # it is find_one because we're looking for only one document (1 user)
        {'_id': ObjectId(_id)},
        {'incoming_requests': 1}
    )
    if result is None:
        return []

    requests = list(map(FriendshipRequest, result['incoming_requests'])) if 'incoming_requests' in result else []
    return requests


def get_outgoing_requests(_id: str) -> list[FriendshipRequest]:
    result = session.users_collection().find_one(
        {'_id': ObjectId(_id)},
        {'outgoing_requests': 1}
    )
    if result is None:
        return []

    requests = list(map(FriendshipRequest, result['outgoing_requests'])) if 'outgoing_requests' in result else []
    return requests


def send_request(my_id: str, friend_id: str) -> bool:

    request_to_friend = FriendshipRequest(user_id=friend_id)
    request_from_me = FriendshipRequest(user_id=my_id)

    query = {'_id': ObjectId(my_id)}  # add request to my outgoing_requests
    update = {'$push': {'outgoing_requests': {
        'user_id': ObjectId(request_to_friend.user_id),
        'sent_at': request_to_friend.sent_at
    }}}
    modified_count = session.users_collection().update_one(query, update).modified_count

    query = {'_id': ObjectId(friend_id)}  # add request to friend's incoming_requests
    update = {'$push': {'incoming_requests': {
        'user_id': ObjectId(request_from_me.user_id),
        'sent_at': request_from_me.sent_at
    }}}
    modified_count += session.users_collection().update_one(query, update).modified_count

    return modified_count == 2


def cancel_request(my_id: str, friend_id: str) -> bool:

    my_id = ObjectId(my_id)
    friend_id = ObjectId(friend_id)

    query = {'_id': my_id}  # delete request instance for me
    update = {'$pull': {'outgoing_requests': {'user_id': friend_id}}}
    modified_count = session.users_collection().update_one(query, update).modified_count

    query = {'_id': friend_id}  # delete request instance for friend
    update = {'$pull': {'incoming_requests': {'user_id': my_id}}}
    modified_count += session.users_collection().update_one(query, update).modified_count

    return modified_count == 2


def decline_request(my_id: str, friend_id: str) -> bool:
    return cancel_request(friend_id, my_id)
    # opposite operation to cancel_request - delete your incoming request, outgoing_request in friend


def accept_request(my_id: str, friend_id: str) -> bool:

    my_id = ObjectId(my_id)
    friend_id = ObjectId(friend_id)

    query = {"_id": my_id}  # add friend to my instance
    update = {"$addToSet": {"friends": friend_id}}
    modified_count = session.users_collection().update_one(query, update).modified_count

    query = {"_id": friend_id}  # add me to friend's instance
    update = {"$addToSet": {"friends": my_id}}
    modified_count += session.users_collection().update_one(query, update).modified_count

    return modified_count == 2


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


def __get_n_best_recommendations(friends, amount) -> list[FriendCloseness]:
    closest_friends = []
    for closeness in friends:
        if len(closest_friends) < amount:
            heapq.heappush(closest_friends, closeness)
        else:
            heapq.heappushpop(closest_friends, closeness)
    return closest_friends


def get_friend_recommendation_profiles(my_id: str, amount: int) -> list[PublicUserModel]:
    my_friends = get_friends(my_id)
    all_recommendations = set()
    for friend in my_friends:
        friend_friends = get_friends(str(friend))
        all_recommendations |= set(map(lambda x: FriendCloseness(x), friend_friends))

    my_friends_set = set(map(FriendCloseness, map(str, my_friends)))
    resulting_recommendations = all_recommendations.difference(my_friends_set)
    resulting_recommendations.discard(FriendCloseness(my_id))

    top_n = sorted(__get_n_best_recommendations(resulting_recommendations, amount), reverse=True)

    id_list = [recommendation.id for recommendation in top_n]

    profiles = [get_public_user(str(friend_id)) for friend_id in id_list]
    return profiles


# Functions related to user profile

def set_about_me(user_id: str, about_me: str) -> bool:
    modified_count = session.users_collection().update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'about_me': about_me}}
    ).modified_count
    return modified_count == 1


def set_profile_pic(user_id: str, profile_pic: str) -> bool:
    modified_count = session.users_collection().update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile_pic': profile_pic}}
    ).modified_count
    return modified_count == 1


def get_profile_pic(user_id: str) -> str | None:
    results = session.users_collection().find_one({'_id': ObjectId(user_id)}, {'profile_pic': 1})
    if results and 'profile_pic' in results:
        return results['profile_pic']
    return None
