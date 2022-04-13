from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from starlette import status

from biz.api.decorator import apiResponse
from biz.api.oauth2 import getCurrentUser, getUserTokenDict
from biz.api.ums.api_user import UserIn
from biz.model.ums import User
from biz.service.dms import dictService
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, TOKEN_URL
from biz.service.ums import userService, ruleService

router = APIRouter()


class Token(BaseModel):
    currentAuthority: str
    accessToken: str
    type: str
    tokenType: str = 'bearer'
    status: str = 'ok'


class OAuth2PasswordIn(BaseModel):
    username: str
    password: str
    autoLogin: Optional[bool]
    type: Optional[str]


# 请求接口
@router.post('/login', response_model=Token)
async def login_for_access_token(json_data: OAuth2PasswordIn):
    """
    用户获取令牌
    :param json_data: 传入的请求体，格式如下： { "username": "admin", "password": "admin", type: "Bearer"}
    :return: 返回用户令牌
    """
    # 首先校验用户信息
    user = userService.getUser(nick=json_data.username)

    if user is None or user.isDelete or user.validity == 'invalid':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户,无法登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not userService.authenticate_user(user, json_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户名密码",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = Token(currentAuthority=user.nick, accessToken=getUserTokenDict(user), type=json_data.type)
    return token


@router.get('/logout')
@apiResponse(message='注销成功')
async def login_out():
    """
    用户注销系统
    :return: 无返回值
    """
    return None


@router.get("/currentUser")
@apiResponse(UserIn, exclude_fields=['password'])
async def getMe(current_user: User = Depends(getCurrentUser)):
    """
    获取当前令牌用户
    :param current_user:
    :return:
    """
    user = current_user
    return user
