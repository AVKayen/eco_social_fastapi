from typing import Annotated
from datetime import datetime, timezone, timedelta

from fastapi import Depends, APIRouter, Form, UploadFile
from fastapi.responses import JSONResponse

from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model
import model.activity_model as activity_model

import utils.file_handler as file_handler

activity_router = APIRouter()


@activity_router.post('/', status_code=201)
async def create_activity(
        token_data: Annotated[TokenData, Depends(parse_token)],
        activity_type: Annotated[activity_model.ActivityType, Form()],
        title: Annotated[str, Form()],
        caption: Annotated[str, Form()] = None,
        images: list[UploadFile] | None = None,
):
    user = user_model.get_user_by_id(token_data.user_id)

    new_last_time_on_streak = datetime.now(timezone.utc)

    if user.last_time_on_streak is None:
        new_streak = 1
    elif datetime.now(timezone.utc) - user.last_time_on_streak.replace(tzinfo=timezone.utc) < timedelta(hours=48):
        new_streak = user.streak + 1
    else:
        new_streak = 1

    points_gained = 100  # To be implemented
    new_points = user.points + points_gained

    image_filenames = []
    if images:
        for uploaded_file in images:
            filename = await file_handler.handle_file_upload(uploaded_file, {'image/jpg', 'image/png', 'image/jpeg'}, 5)
            image_filenames.append(filename)

    new_activity = activity_model.NewActivityModel(
        user_id=token_data.user_id,
        activity_type=activity_type,
        title=title,
        caption=caption,
        streak_snapshot=new_streak,
        points_gained=points_gained,
        images=image_filenames
    )

    activity_model.create_activity(new_activity)
    user_model.update_after_activity_creation(
        user_id=token_data.user_id,
        new_points=new_points,
        new_streak=new_streak,
        new_last_time_on_streak=new_last_time_on_streak
    )
