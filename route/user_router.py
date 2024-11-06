from typing import Annotated

from fastapi import Depends, APIRouter

from model.request_body_model import UserIdBody
from model.response_model import ResponseModel
from controller.auth_controller import TokenData, parse_token
import model.user_model as user_model


user_router = APIRouter()


@user_router.post('/invitation/send')
def invite_user(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]):

    if token_data.user_id == body.user_id:
        return ResponseModel(status='You cannot send an invitation to yourself')
    if user_model.is_request_outgoing(token_data.user_id, body.user_id):
        return ResponseModel(status='Invitation request already sent to that person')
    if user_model.is_request_incoming(token_data.user_id, body.user_id):
        return ResponseModel(status='Invitation request already incoming from that person')

    if user_model.send_request(token_data.user_id, body.user_id):
        return ResponseModel.success()
    return ResponseModel.error()


@user_router.delete('/invitation/cancel/', response_model=ResponseModel)
def cancel_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]):
    if user_model.cancel_request(token_data.user_id, body.user_id):
        return ResponseModel.success()
    return ResponseModel(status='No invitation to cancel or something went wrong')


@user_router.post('/invitation/accept/', response_model=ResponseModel)
def accept_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]):

    if not user_model.is_request_incoming(token_data.user_id, body.user_id):
        return ResponseModel(status='No invitation to accept')

    deletion_success = user_model.decline_request(token_data.user_id, body.user_id)

    if deletion_success and user_model.accept_request(token_data.user_id, body.user_id):
        return ResponseModel.success()
    return ResponseModel(status='Already friends or something went wrong')


@user_router.delete('/invitation/decline/', response_model=ResponseModel)
def decline_invitation(body: UserIdBody, token_data: Annotated[TokenData, Depends(parse_token)]):

    if not user_model.is_request_incoming(token_data.user_id, body.user_id):
        return ResponseModel(status='No invitation to decline')

    if user_model.decline_request(token_data.user_id, body.user_id):
        return ResponseModel.success()
    return ResponseModel.error()


@user_router.get('/me/')
def me(token_data: Annotated[TokenData, Depends(parse_token)]) -> user_model.UserModel | ResponseModel:
    user = user_model.get_user_by_id(token_data.user_id)
    if not user:
        return ResponseModel(status='Could not find your profile data')
    return user


@user_router.get('/{user_id}/')
def get_user(
        user_id: str, token_data: Annotated[TokenData, Depends(parse_token)]
) -> user_model.PublicUserModel | user_model.PrivateUserModel | ResponseModel:

    if user_model.is_user_friend(token_data.user_id, user_id):
        user = user_model.get_private_user(user_id)
    else:
        user = user_model.get_public_user(user_id)

    if not user:
        return ResponseModel(status='Could not find profile data')
    return user
