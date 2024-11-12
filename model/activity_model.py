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
    train_instead_of_car = 14

    plant_tree = 21
    plant_other = 22

    buy_local = 31
    buy_second_hand = 32
    sell_unused = 33

    reduce_water = 41
    reduce_energy = 42
    reduce_food_waste = 43

    other = 0


activity_points = {
    ActivityType.trash_picking: 400,

    ActivityType.pub_transport_instead_of_car: 100,
    ActivityType.train_instead_of_car: 100,
    ActivityType.bike_instead_of_car: 300,
    ActivityType.walk_instead_of_car: 300,

    ActivityType.plant_tree: 1000,
    ActivityType.plant_other: 500,

    ActivityType.buy_local: 200,
    ActivityType.buy_second_hand: 200,
    ActivityType.sell_unused: 400,

    ActivityType.reduce_water: 150,
    ActivityType.reduce_energy: 150,
    ActivityType.reduce_food_waste: 100,

    ActivityType.other: 0

}


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
    id: Annotated[ObjectId, ObjectIdPydanticAnnotation] = Field(alias='_id')

    model_config = ConfigDict(populate_by_name=True)


def create_activity(activity: NewActivityModel):
    inserted_id = session.activities_collection().insert_one(activity.model_dump()).inserted_id
    return inserted_id


def get_activity_by_id(activity_id: str) -> ActivityModel | None:
    result: dict[str, Any] | None = session.activities_collection().find_one({'_id': ObjectId(activity_id)})

    if result is None:
        return None

    return ActivityModel(**result)


def update_activity(activity_id: str, title: str, caption: str, images: list[str]) -> bool:
    modified_count = session.activities_collection().update_one(
        {'_id': ObjectId(activity_id)},
        {'$set': {
            'title': title,
            'caption': caption,
            'images': images
        }}
    ).modified_count
    return modified_count == 1


def delete_activity(activity_id: str, user_id: str) -> bool:
    deleted_count = session.activities_collection().delete_one({'_id': ObjectId(activity_id)}).deleted_count
    modified_count = session.users_collection().update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'activities': ObjectId(activity_id)}}
    ).modified_count
    return deleted_count == 1 and modified_count == 1


def get_user_activities(user_id: str) -> list[ActivityModel]:
    results = session.activities_collection().find({'user_id': ObjectId(user_id)}).sort('created_at', -1)

    if results is None:
        return []

    activities = [ActivityModel(**result) for result in results]
    return activities


def get_feed(user_id: str) -> list[ActivityModel]:
    friends = get_user_by_id(user_id).friends

    results = session.activities_collection().find({'user_id': {'$in': friends}}).sort('created_at', -1)
    if results is None:
        return []

    activities = [ActivityModel(**result) for result in results]
    return activities
