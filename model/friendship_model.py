from pydantic import BaseModel, Field
from typing import Optional
from datetime import UTC, datetime

from route.user_router import me


from db.session import session


class FriendshipRequest(BaseModel):
    #me().id -> user's id
    friend_id: str
    sent_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    def cancel_request(self)-> str:
        query = {"_id": me().id}
        update = { "$pull": { "incoming_requests": { "$in": [self.friend_id]}}}
        result = session.users_collection().update_one(query,update) #should it not work -> change to update_many
        return str(result)  #is a return value needed?

    def approve_request(self)-> str:
        query = {"_id": me().id}
        update = {"$push": {"friends": self.friend_id}}
        self.cancel_request()
        inserted_friend = session.users_collection().update_one(query, update)
        return str(inserted_friend['_id'])


def get_friends() -> list[str] | None:
    result = me.friends
    if result is None:
        return None
    return result

def get_incoming_requests() -> list[FriendshipRequest] | None:
    result = me.incoming_requests
    if result is None:
        return None
    return result

def get_outgoing_requests() -> list[FriendshipRequest] | None:
    result = me.outgoing_requests
    if result is None:
        return None
    return result

def delete_friend(friend_id) -> str:
    query = {"_id": me().id}
    update = { "$pull": { "friends": { "$in": [friend_id]}}}
    result = session.users_collection().update_one(query,update) #should it not work -> change to update_many
    return str(result)  #is a return value needed?