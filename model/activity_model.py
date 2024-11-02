from pydantic import BaseModel, Field
from enum import IntEnum


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


class ActivityModel(BaseModel):
    _id: str = Field(alias='_id')
    activity_type: ActivityType
    title: str
    caption: str
    images: list[str]
