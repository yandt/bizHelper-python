from datetime import datetime
from typing import List

import jaydebeapi
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic.class_validators import Optional

from analyse.conf import jdbc
from analyse.dbpool import Dbpool
from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.api.oauth2 import getCurrentUser, getCurrentUserId
from biz.model.grid import Connect
from biz.service.grid import connectService
from common import entityUtils

router = APIRouter(prefix="/connect")


class ConnectIn(BaseModel):
    connectId: Optional[int]
    name: str
    drive: str
    connectStr: str
    username: str
    password: str
    createUid: Optional[int]
    visibility: str
    validity: str
    attribute: Optional[dict]
    insertTime: Optional[datetime]
    modifyTime: Optional[datetime]

    class Config:
        orm_mode = True


class DriveIn(BaseModel):
    label: str
    value: str
    connectStr: str


@router.get("/list")
@apiResponse(List[ConnectIn], exclude_fields=['password', 'username'])
async def getList(validity: str = None, uid: int = Depends(getCurrentUserId)):
    """
    获取数据库连接列表
    :param uid: 用户ID
    :param validity: 有效性
    :return:
    """
    connect_list = connectService.getList(uid, validity)
    return connect_list


@router.get("/page_list")
@apiResponse(List[ConnectIn], exclude_fields=['password', 'username'])
async def getPageList(current: int, pageSize: int, keyword: str = '', uid: int = Depends(getCurrentUserId)):
    """
    获取数据库连接列表
    :param current:
    :param pageSize:
    :param keyword:
    :return:
    """
    page_list = connectService.getPageList(uid, current, pageSize, keyword)
    return page_list


@router.get("/drive_list")
@apiResponse(List[DriveIn])
async def getDriveList():
    """
    获取数据库连接驱动列表
    :return:
    """
    return [{
        "label": j,
        "value": j,
        "connectStr": jdbc[j].get('connectStr')
    } for j in jdbc]


@router.put('')
@apiResponse(ConnectIn, message='连接[ {name} ]保存成功')
async def save(conn: ConnectIn, uid: int = Depends(getCurrentUserId)):
    """
    保存数据库连接
    :param uid:
    :param conn:
    :return:
    """
    r = Connect()
    entityUtils.copy(conn, r)
    r.createUid = uid
    connectService.save(r)
    return r


@router.delete('')
@apiResponse(message='数据库连接删除成功')
async def delete(connectId: int):
    """
    删除数据库连接
    :param connectId:
    :return:
    """
    count = connectService.delete(connectId)
    return count


@router.get("")
@apiResponse(ConnectIn)
async def getConnect(connectId: int):
    """
    获取指定ID的角色信息
    :param connectId:
    :return:
    """
    return connectService.getConnect(connectId)


@router.put("/test")
@apiResponse()
async def testConnect(connect: ConnectIn):
    dbpool = None
    try:
        dbpool = Dbpool(connect.drive, connect.connectStr, connect.username, connect.password)
    except Exception as e:
        return {'isConn': False, 'message': str(e)}
    finally:
        if dbpool is not None:
            dbpool.close()
        return {'isConn': True}
