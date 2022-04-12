from datetime import datetime
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.model.ums import Role
from biz.service.ums import roleService
from common import entityUtils

router = APIRouter(prefix="/role")


class RoleIn(BaseModel):
    roleId: Optional[int]
    name: str
    type: str
    attribute: Optional[dict]
    validity: str
    insertTime: Optional[datetime]

    class Config:
        orm_mode = True


@router.get("/list/{type}")
@apiResponse(List[RoleIn], exclude_fields=['attribute'])
async def getList(type: str):
    """
    获取指定角色类型列表
    :param type: 类型
    :return:
    """
    role_list = roleService.getList(type)
    return role_list


@router.get("/page_list")
@apiResponse(List[RoleIn])
async def getPageList(current: int, pageSize: int, keyword: str = '', type: str = 'function'):
    """
    获取角色页列表
    :param current:
    :param pageSize:
    :param keyword:
    :param type:
    :return:
    """
    page_list = roleService.getPageList(current, pageSize, keyword, type)
    return page_list


@router.put('')
@apiResponse(RoleIn, message='角色[ {name} ]保存成功')
async def save(role: RoleIn):
    """
    保存角色
    :param role:
    :return:
    """
    r = Role()
    entityUtils.copy(role, r)
    roleService.save(r)
    return r


@router.delete('')
@apiResponse(message='角色删除成功')
async def delete(roleId: int):
    """
    删除角色
    :param roleId:
    :return:
    """
    count = roleService.delete(roleId)
    return count


@router.get("")
@apiResponse(RoleIn)
async def getRole(roleId: int):
    """
    获取指定ID的角色信息
    :param roleId:
    :return:
    """
    return roleService.getRole(roleId)
