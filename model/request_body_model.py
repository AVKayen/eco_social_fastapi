from pydantic import BaseModel, constr
from model.activity_model import ActivityBaseModel
from fastapi import UploadFile


class UserIdBody(BaseModel):
    user_id: constr(min_length=24, max_length=24)


class AboutMeBody(BaseModel):
    about_me: constr(max_length=256)


class ActivityBody(ActivityBaseModel):
    images: list[UploadFile]
