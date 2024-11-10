from pydantic import BaseModel, Field, ConfigDict
from enum import IntEnum
from bson import ObjectId
from typing import Annotated

from db.session import session
from model.object_id_model import ObjectIdPydanticAnnotation


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
