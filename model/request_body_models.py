from pydantic import BaseModel


class UserIdBody(BaseModel):
    user_id: str
