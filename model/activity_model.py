from pydantic import BaseModel, Field, ConfigDict
from enum import IntEnum
from bson import ObjectId
from typing import Annotated, Any
from datetime import datetime, timezone

from db.session import session
from model.object_id_model import ObjectIdPydanticAnnotation
from model.user_model import get_user_by_id


class ActivityType(IntEnum):
    trash_picking = 1

    pub_transport_instead_of_car = 11
    bike_instead_of_car = 12
    walk_instead_of_car = 13
    train_instead_of_plane = 14

    plant_tree = 21
    plant_other = 22

    buy_local = 31
    buy_second_hand = 32
    sell_unused = 33

    reduce_water = 41
    reduce_energy = 42
    reduce_food_waste = 43

    other = 0


class ActivityBaseModel(BaseModel):
    activity_type: ActivityType
    title: str
    caption: str | None = ''
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NewActivityModel(ActivityBaseModel):
    user_id: Annotated[ObjectId, ObjectIdPydanticAnnotation]
    points_gained: int
    streak_snapshot: int
    images: list[str] = []


class ActivityModel(NewActivityModel):
    id: str = Field(alias='_id')

    model_config = ConfigDict(populate_by_name=True)


def create_activity(activity: NewActivityModel):
    inserted_id = session.activities_collection().insert_one(activity.model_dump()).inserted_id
    print(inserted_id)
    return inserted_id


def get_activity_by_id(activity_id: str) -> ActivityModel | None:
    result: dict[str, Any] | None = session.activities_collection().find_one({'_id': ObjectId(activity_id)})

    if result is None:
        return None

    return ActivityModel(**result)


def get_user_activities(user_id: str) -> list[ActivityModel]:
    activity_ids = get_user_by_id(user_id).activities
    result = [get_activity_by_id(activity_id) for activity_id in activity_ids]

    return result


def get_feed(user_id: str) -> list[ActivityModel]:
    friends = get_user_by_id(user_id).friends

    feed: list[ActivityModel] = []
    for friend in friends:
        feed.extend(get_user_activities(str(friend)))
    feed.sort(key = lambda activity: activity.created_at, reverse = True)
    return feed
