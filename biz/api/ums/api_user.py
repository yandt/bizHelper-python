import datetime
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.api.model import ResultModel
from biz.api.ums.api_company import CompanyIn
from biz.constant import DICT_PATH_DEFAULT_PASSWORD
from biz.model.ums import User
from biz.service.dms import dictService
from biz.service.ums import userService
from common import entityUtils

router = APIRouter(prefix="/user")


class UserIn(BaseModel):
    uid: Optional[int]
    nick: str
    name: str
    email: Optional[str]
    mobile: Optional[str]
    avatar: Optional[str]
    attribute: Optional[dict]
    validity: Optional[str]
    insertTime: Optional[datetime.datetime]
    companyId: Optional[int]
    company: Optional[CompanyIn]
    password: Optional[str]
    front: Optional[dict]
    defined: Optional[list[str]]
    isAdmin: Optional[bool]

    class Config:
        orm_mode = True


@router.get("/list")
@apiResponse(List[UserIn], exclude_fields=set(['password']))
async def getList(current: int, pageSize: int, keyword: str = '', isDelete: bool = False):
    user_list = userService.getUserList(current, pageSize, keyword, validity=None, isDelete=isDelete)
    return user_list


@router.put('')
@apiResponse(UserIn, message='用户[{nick}]保存成功')
async def save(user: UserIn):
    if user.uid is None:
        u = userService.getUser(nick=user.nick)
        if u is not None:
            raise ApiException(message='用户名%s已存在，请改变用户名' % user.nick)
        default_password = dictService.getDictByPath(DICT_PATH_DEFAULT_PASSWORD).value
        u = User()
        entityUtils.copy(user, u)
        u = userService.save(u, default_password)
        return u
    else:
        u = userService.getUser(uid=user.uid)
        if u is None or u.isDelete:
            raise ApiException(message='用户不存在，无法修改' % user.nick)
        entityUtils.copy(user, u)
        userService.save(u)
        return u


@router.put('/password')
@apiResponse(UserIn, message='用户{nick}密码保存成功')
async def save(user: UserIn):
    if user.uid is None:
        raise ApiException(message='缺少用户ID,无法修改' % user.nick)
    else:
        u = userService.getUser(uid=user.uid)
        if u is None or u.isDelete:
            raise ApiException(message='用户不存在，无法修改' % user.nick)
    entityUtils.copy(user, u)
    userService.save(u, user.password)
    return user


@router.delete('')
@apiResponse(message='用户删除成功')
async def delete(uid: int):
    count = userService.delete(uid)
    return count

