from typing import Annotated

from fastapi import Depends, APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from model.request_model import UserIdBody, AboutMeBody
from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model
from pydantic import Field

import utils.file_handler as file_handler


user_router = APIRouter()


@user_router.post('/invitation/send', status_code=201)
def invite_user(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]) -> None:

    if token_data.user_id == body.user_id:
        raise HTTPException(400, 'You cannot send an invitation to yourself')
    if user_model.is_request_outgoing(token_data.user_id, body.user_id):
        raise HTTPException(400, 'Invitation request already sent to that person')
    if user_model.is_request_incoming(token_data.user_id, body.user_id):
        raise HTTPException(400, 'Invitation request already incoming from that person')
    if user_model.is_user_friend(token_data.user_id, body.user_id):
        raise HTTPException(400, 'You are already friends')

    if not user_model.send_request(token_data.user_id, body.user_id):
        raise HTTPException(400)


@user_router.delete('/invitation/cancel/')
def cancel_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]) -> None:
    if not user_model.cancel_request(token_data.user_id, body.user_id):
        raise HTTPException(400)  # 'No invitation to cancel or something went wrong'


@user_router.post('/invitation/accept/', status_code=201)
def accept_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]) -> None:

    if not user_model.is_request_incoming(token_data.user_id, body.user_id):
        raise HTTPException(400, 'No invitation to accept')

    deletion_success = user_model.decline_request(token_data.user_id, body.user_id)

    if not deletion_success or not user_model.accept_request(token_data.user_id, body.user_id):
        raise HTTPException(400)  # 'Already friends or something went wrong'


@user_router.delete('/invitation/decline/')
def decline_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]) -> None:

    if not user_model.is_request_incoming(token_data.user_id, body.user_id):
        raise HTTPException(400, 'No invitation to decline')

    if not user_model.decline_request(token_data.user_id, body.user_id):
        raise HTTPException(400)


@user_router.get('/my-profile/')
def get_my_profile(token_data: Annotated[TokenData, Depends(parse_token)]) -> user_model.UserModel:
    user = user_model.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(404)
    return user


@user_router.post('/about-me/')
def set_about_me_section(body: AboutMeBody, token_data: Annotated[TokenData, Depends(parse_token)]):
    if not user_model.set_about_me(token_data.user_id, body.about_me):
        raise HTTPException(400)


@user_router.post('/profile-pic/')
async def set_profile_picture(
        file: UploadFile, token_data: Annotated[TokenData, Depends(parse_token)], background_tasks: BackgroundTasks
) -> JSONResponse:

    accepted_mime_types = {'image/jpeg'}
    filename = file_handler.handle_file_upload(file, accepted_mime_types, 5)
    await file_handler.save_uploaded_file(file, filename)

    prev_filename = user_model.get_profile_pic(token_data.user_id)
    if prev_filename:
        background_tasks.add_task(file_handler.delete_uploaded_file, prev_filename)

    if not user_model.set_profile_pic(token_data.user_id, filename):
        raise HTTPException(400)
    return JSONResponse({'uploaded_file': filename})


@user_router.delete('/profile-pic')
def delete_profile_picture(token_data: Annotated[TokenData, Depends(parse_token)], background_tasks: BackgroundTasks):
    prev_filename = user_model.get_profile_pic(token_data.user_id)
    if not prev_filename:
        raise HTTPException(404)
    background_tasks.add_task(file_handler.delete_uploaded_file, prev_filename)

    if not user_model.set_profile_pic(token_data.user_id, ''):
        raise HTTPException(400)


@user_router.get('/{user_id}/')
def get_user(
        user_id: str, token_data: Annotated[TokenData, Depends(parse_token)]
) -> user_model.PublicUserModel | user_model.PrivateUserModel:

    if user_model.is_user_friend(token_data.user_id, user_id):
        user = user_model.get_private_user(user_id)
    else:
        user = user_model.get_public_user(user_id)

    if not user:
        raise HTTPException(404)
    return user


@user_router.get('/friend-recommendations/{amount}/')
def get_friend_recommendations(
        amount: Annotated[int, Field(le=10)], token_data: Annotated[TokenData, Depends(parse_token)]
) -> list[user_model.PublicUserModel]:

    friend_recommendations = user_model.get_friend_recommendation_profiles(token_data.user_id, amount)
    return friend_recommendations
