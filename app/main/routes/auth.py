from fastapi.routing import APIRouter
from typing import Annotated
from fastapi import Request, Body, Depends
from app.main.factories import (
    make_db_auth_login,
    make_db_update_password
)
from app.schemas.common import MessageResponse
from app.schemas.auth import UserLogin, LoginOut, PasswordUpdate
from app.main.exceptions import RequiredRequestBody, InvalidUuid
from app.infra.auth import JwtBearer
from app.main.config import PREFIX
from bson import ObjectId


router = APIRouter(prefix=f"{PREFIX}/auth", tags=['Auth'])


@router.post(
    "/login",
    status_code=200,
    summary="Login a Profile",
    response_description="Profile Logged",
    response_model=LoginOut
)
async def login(request: Request, data: Annotated[UserLogin, Body()]):
    if not data:
        raise RequiredRequestBody()

    db_auth_login = make_db_auth_login(request)
    user = await db_auth_login.login(data)

    return LoginOut(message="Login successfully", data=user)


@router.put(
    "/update-password",
    status_code=200,
    summary="Update User Password",
    response_description="User Password Updated",
    response_model=MessageResponse
)
async def update_password(
    uuid: Annotated[str, Depends(JwtBearer())],
    data: Annotated[PasswordUpdate, Body()]
):
    if not data:
        raise RequiredRequestBody()

    if not ObjectId.is_valid(uuid):
        raise InvalidUuid("user")

    data.uuid = uuid
    db_update_password = make_db_update_password()
    await db_update_password.update_password(data)

    return MessageResponse(message="User password successfully updated")
