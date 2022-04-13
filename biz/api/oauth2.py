from datetime import timedelta, datetime

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt import PyJWTError
from starlette import status

from biz.constant import DICT_PATH_DEFAULT_PASSWORD, DICT_PATH_ADMIN_NICK
from biz.model.ums import User
from biz.service.dms import dictService
from biz.service.ums import ruleService
from biz.service.ums.userService import getUser
from config import SECRET_KEY, ALGORITHM, TOKEN_URL, ACCESS_TOKEN_EXPIRE_MINUTES


# 生成token
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    创建用户令牌
    :param data: 生成令牌的信息，包括用户名及授权信息
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def getUserTokenDict(user: User):
    """
    生成用户授权信息的dict
    :param user:
    :return:
    """
    rule_list = ruleService.getFrontRuleListByUserId(user.uid)
    front_rules = {}
    defined_rules = []
    back_rules = {}
    for r in rule_list:
        if r.type == 'front':
            front_rules[r.path] = r.hasRule if r.hasRule == 1 else 0
        elif r.type == 'defined' and r.hasRule == 1:
            defined_rules.append(r.path)
        elif r.type == 'back':
            back_rules[r.path] = r.hasRule if r.hasRule == 1 else 0

    user.front = front_rules
    user.defined = defined_rules
    user.back = back_rules
    admin_nick = dictService.getDictByPath(DICT_PATH_ADMIN_NICK).value   # 从数据字典获取指定的管理员用户名
    if user.nick == admin_nick:
        user.isAdmin = True

    # TODO 此处设置权限为通过token保存权限方案，此方法会减少服务器损耗，但缺点是：
    #  大大加长传到客户端的TOKEN长度，同时客户权限改变后必须要重新登录，
    #  后期计划完善，可以自由选择，一是使用此方法，二是使用session,用redis存储权限方案

    # 生成并返回token信息
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_dict = create_access_token(
        data={"nick": user.nick,
              "front": user.front,  # 前端权限路径
              "defined": user.defined,  # 自定义权限代码
              "back": user.back,  # 后端权限路径
              "isAdmin": user.nick == admin_nick},
        expires_delta=access_token_expires
    )
    return access_token_dict


async def getCurrentUser(token: str = Depends(OAuth2PasswordBearer(tokenUrl=TOKEN_URL))):
    """
    通过加密TOKEN获取当前用户信息
    :param token:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("nick")
        if username is None:
            raise credentials_exception
    except PyJWTError as e:
        raise credentials_exception
    user = getUser(nick=username)
    user.front = payload.get('front')
    user.defined = payload.get('defined')
    user.isAdmin = payload.get('isAdmin')
    user.back = payload.get('back')

    if user is None:
        raise credentials_exception
    return user


async def getUserOnRequest(request: Request):
    """
    通过request获取用户信息
    :param request:
    :return:
    """
    authorization: str = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    user = await getCurrentUser(token)
    return user;
