from pydantic import BaseModel, Field
from typing import Optional
from datetime import UTC, datetime

from model.user_model import UserModel
from route.user_router import me, user_router

from db.session import session


class FriendshipRequest(BaseModel):
    #should it not work -> change update_one to update_many   #if no return value is needed, delete the result instances
    friend_id: str
    sent_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    def send_request(self) -> str:
        query = {"_id": me().id} #add request to my outgoing_requests
        update = {"$push": {"outgoing_requests": self.friend_id}}
        user_result = session.users_collection().update_one(query,update)

        query = {"_id": self.friend_id} #add request to friend's incoming_requests
        update = {"$push": {"incoming_requests": me().id}}
        friend_result = session.users_collection().update_one(query,update)

        user_result = str(user_result)
        friend_result = str(friend_result)
        return str(user_result + friend_result)

    def cancel_request(self) -> str:
        query = {"_id": me().id} #delete request instance for me
        update = { "$pull": { "outgoing_requests": { "$in": [self.friend_id]}}}
        user_result = session.users_collection().update_one(query,update)

        query = {"_id": self.friend_id} #delete request instance for friend
        update = { "$pull": { "incoming_requests": { "$in": [me().id]}}}
        friend_result = session.users_collection().update_one(query,update)

        user_result = str(user_result)
        friend_result = str(friend_result)
        return str(user_result + friend_result)

    def disapprove_request(self) -> str:
        query = {"_id": me().id} #delete request instance for me
        update = { "$pull": { "incoming_requests": { "$in": [self.friend_id]}}}
        user_result = session.users_collection().update_one(query,update)

        query = {"_id": self.friend_id} #delete request instance for friend
        update = { "$pull": { "outgoing_requests": { "$in": [me().id]}}}
        friend_result = session.users_collection().update_one(query,update)

        user_result = str(user_result)
        friend_result = str(friend_result)
        return str(user_result + friend_result)

    def approve_request(self) -> str:
        query = {"_id": me().id} #add friend to my instance
        update = {"$push": {"friends": self.friend_id}}
        inserted_friend = session.users_collection().update_one(query, update)

        query = {"_id": self.friend_id} #add me to friend's instance
        update = {"$push": {"friends": me().id}}
        inserted_self = session.users_collection().update_one(query, update)

        self.disapprove_request() #remove requests

        inserted_friend = str(inserted_friend)
        inserted_self = str(inserted_self)
        return str(inserted_friend + inserted_self)

    def delete_friend(self) -> str:
        query = {"_id": me().id} #delete friend instance for me
        update = { "$pull": { "friends": { "$in": [self.friend_id]}}}
        user_result = session.users_collection().update_one(query,update)

        query = {"_id": self.friend_id} #delete request instance for friend
        update = { "$pull": { "friends": { "$in": [me().id]}}}
        friend_result = session.users_collection().update_one(query,update)

        user_result = str(user_result)
        friend_result = str(friend_result)
        return str(user_result + friend_result)


def get_friends(user: UserModel) -> list[str] | None:
    result = user.friends
    if result is None:
        return None
    return result

def get_incoming_requests(user: UserModel) -> list[FriendshipRequest] | None:
    result = user.incoming_requests
    if result is None:
        return None
    return result

def get_outgoing_requests(user: UserModel) -> list[FriendshipRequest] | None:
    result = user.outgoing_requests
    if result is None:
        return None
    return result