from typing import Annotated
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from fastapi import Depends, APIRouter, Form, UploadFile, HTTPException, BackgroundTasks

from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model
import model.activity_model as activity_model
from model.request_model import ObjectIdStr

import utils.file_handler as file_handler
from config.settings import settings


ACCEPTED_MIME_TYPES = {'image/jpg', 'image/png', 'image/jpeg'}


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

    points_gained = activity_model.activity_points[activity_type] or 0
    new_points = user.points + points_gained

    image_filenames = []
    if images:
        for uploaded_file in images:
            filename = file_handler.handle_file_upload(uploaded_file, ACCEPTED_MIME_TYPES)
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
    if images:
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

    if user_id != token_data.user_id and not user_model.is_user_friend(token_data.user_id, user_id):
        raise HTTPException(403)

    activities = activity_model.get_user_activities(user_id)
    return activities


@activity_router.get('/{activity_id}')
def get_activity(
        activity_id: ObjectIdStr, token_data: Annotated[TokenData, Depends(parse_token)]
) -> activity_model.ActivityModel:
    activity = activity_model.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(404)

    activity_owner = str(activity.user_id)
    if activity_owner != token_data.user_id and not user_model.is_user_friend(token_data.user_id, activity_owner):
        raise HTTPException(403)
    return activity


@activity_router.patch('/{activity_id}')
async def update_activity(
        background_taks: BackgroundTasks,
        activity_id: ObjectIdStr,
        token_data: Annotated[TokenData, Depends(parse_token)],
        title: Annotated[str, Form()] | None = None,
        caption: Annotated[str, Form()] | None = None,
        new_images: list[UploadFile] | None = None,
        images_to_delete: list[str] | None = None
):
    activity = activity_model.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(404)
    if str(activity.user_id) != token_data.user_id:
        raise HTTPException(403)

    if new_images is None:
        new_images = []
    if images_to_delete is None:
        images_to_delete = []

    if len(activity.images) + len(new_images) - len(images_to_delete) > settings.max_images_per_activity:
        raise HTTPException(400, f'Exceeeded the maximum number of images per activity '
                                 f'({settings.max_images_per_activity}).')

    new_filenames = []
    for uploaded_image in new_images:
        filename = file_handler.handle_file_upload(uploaded_image, ACCEPTED_MIME_TYPES)
        new_filenames.append(filename)

    title = title or activity.title
    caption = caption or activity.caption
    images = list(set(activity.images).union(set(new_filenames)).difference(set(images_to_delete)))

    activity_model.update_activity(activity_id, title, caption, images)

    for new_image, new_filename in zip(new_images, new_filenames):
        await file_handler.save_uploaded_file(new_image, new_filename)

    for filename in images_to_delete:
        background_taks.add_task(file_handler.delete_uploaded_file, filename)


@activity_router.delete('/{activity_id}')
def delete_activity(activity_id: ObjectIdStr, token_data: Annotated[TokenData, Depends(parse_token)]):
    activity = activity_model.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(404)
    activity_owner = str(activity.user_id)
    if activity_owner != token_data.user_id:
        raise HTTPException(403)

    activity_points = activity.points_gained
    user_model.increment_user_points(token_data.user_id, -activity_points)
    activity_model.delete_activity(activity_id)
