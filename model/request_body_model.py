from pydantic import BaseModel, constr


class UserIdBody(BaseModel):
    user_id: constr(min_length=24, max_length=24)


class AboutMeBody(BaseModel):
    about_me: constr(max_length=64)
