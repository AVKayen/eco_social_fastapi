from typing import Annotated
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from fastapi import Depends, APIRouter, Form, UploadFile, HTTPException

from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model
import model.activity_model as activity_model
from model.request_model import ObjectIdStr

import utils.file_handler as file_handler
from config.settings import settings


activity_router = APIRouter()


@activity_router.post('/', status_code=201)
async def create_activity(
        token_data: Annotated[TokenData, Depends(parse_token)],
        activity_type: Annotated[activity_model.ActivityType, Form()],
        title: Annotated[str, Form()],
        caption: Annotated[str, Form()] = None,
        images: list[UploadFile] | None = None,
):
    if images and len(images) > settings.max_images_per_activity:
        raise HTTPException(400, f'Too many files uploaded: {len(images)}. Max {settings.max_images_per_activity}.')

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
            filename = file_handler.handle_file_upload(uploaded_file, {'image/jpg', 'image/png', 'image/jpeg'})
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

    activity_id = activity_model.create_activity(new_activity)

    user_model.update_after_activity_creation(
        user_id=token_data.user_id,
        new_points=new_points,
        new_streak=new_streak,
        new_last_time_on_streak=new_last_time_on_streak,
        activity_id=activity_id
    )

    for uploaded_file, filename in zip(images, image_filenames):
        await file_handler.save_uploaded_file(uploaded_file, filename)


@activity_router.get('/feed')
def get_feed(
        token_data: Annotated[TokenData, Depends(parse_token)]
) -> list[activity_model.ActivityModel]:
    feed = activity_model.get_feed(token_data.user_id)

    return feed


@activity_router.get('/activities/{user_id}')
def get_activities(
        user_id: ObjectIdStr, token_data: Annotated[TokenData, Depends(parse_token)]
) -> list[activity_model.ActivityModel]:
    activities = activity_model.get_user_activities(user_id)

    return activities


@activity_router.get('/{activity_id}')
def get_activity(
        activity_id: ObjectIdStr, token_data: Annotated[TokenData, Depends(parse_token)]
) -> activity_model.ActivityModel:
    activity = activity_model.get_activity_by_id(activity_id)
    activity_owner = str(activity.user_id)
    if activity_owner != token_data.user_id and not user_model.is_user_friend(token_data.user_id, activity_owner):
        raise HTTPException(403)
    return activity
