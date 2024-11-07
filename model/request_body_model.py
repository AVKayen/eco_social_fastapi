from pydantic import BaseModel, constr


class UserIdBody(BaseModel):
    user_id: constr(min_length=24, max_length=24)
