from pydantic import BaseModel, Field
from typing import Annotated


ObjectIdStr = Annotated[str, Field(min_length=24, max_length=24)]


class UserIdBody(BaseModel):
    user_id: ObjectIdStr


class AboutMeBody(BaseModel):
    about_me: ObjectIdStr
