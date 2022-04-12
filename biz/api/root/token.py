from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from starlette import status

from biz.api.decorator import apiResponse
from biz.api.ums.api_user import UserIn
from biz.model.ums import User
from biz.service.ums.userService import getCurrentUser
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, TOKEN_URL
from biz.service.ums import userService

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


# 生成token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
    # 生成并返回token信息
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": json_data.username}, expires_delta=access_token_expires
    )
    token = Token(currentAuthority=json_data.username, accessToken=access_token, type=json_data.type)
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
@apiResponse(UserIn)
async def getMe(current_user: User = Depends(getCurrentUser)):
    """
    获取当前令牌用户
    :param current_user:
    :return:
    """
    return current_user
