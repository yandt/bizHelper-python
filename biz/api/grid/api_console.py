from datetime import datetime
from typing import List
import socketio

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from pydantic.class_validators import Optional

from analyse.dbpool import Dbpool
from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.api.oauth2 import getCurrentUser, getCurrentUserId
from biz.model.grid import Console, Connect
from biz.service.grid import consoleService, connectService
from common import entityUtils

# from main import app
# from main import socket_manager as sm

router = APIRouter(prefix="/console")


class ConsoleIn(BaseModel):
    consoleId: Optional[int]
    connectId: int
    parentId: Optional[int]
    name: str
    dbname: Optional[str]
    content: Optional[str]
    comment: Optional[str]
    createUid: Optional[int]
    attribute: Optional[dict]
    children: Optional[List]
    insertTime: Optional[datetime]
    isFolder: Optional[int]
    children: Optional[List]

    class Config:
        orm_mode = True


class ConsoleExecuteIn(BaseModel):
    consoleId: int
    content: str

    class Config:
        orm_mode = True



@router.get("/list")
@apiResponse(List[ConsoleIn], exclude_fields=['content'])
async def getList(validity: str = None, uid: int = Depends(getCurrentUserId)):
    """
    获取数据库连接列表
    :param uid: 用户ID
    :param validity: 有效性
    :return:
    """
    console_list = consoleService.getList(uid, validity)
    return console_list


@router.get("/tree")
@apiResponse(List[ConsoleIn], exclude_fields=['content'])
async def getTree(validity: str = None, uid: int = Depends(getCurrentUserId)):
    """
    获取数据库连接列表
    :param uid: 用户ID
    :param validity: 有效性
    :return:
    """
    console_list = consoleService.getTree(uid, validity)
    return console_list


@router.get("/page_list")
@apiResponse(List[ConsoleIn])
async def getPageList(current: int, pageSize: int, keyword: str = '', uid: int = Depends(getCurrentUserId)):
    """
    获取数据库连接列表
    :param uid:
    :param current:
    :param pageSize:
    :param keyword:
    :return:
    """
    page_list = consoleService.getPageList(uid, current, pageSize, keyword)
    return page_list


@router.put('')
@apiResponse(ConsoleIn, message='控制台[ {name} ]保存成功')
async def save(conn: ConsoleIn, uid: int = Depends(getCurrentUserId)):
    """
    保存数据库连接
    :param uid:
    :param conn:
    :return:
    """
    r = Console()
    entityUtils.copy(conn, r)
    r.createUid = uid
    r.type = 'node'
    consoleService.save(r)
    return r


@router.delete('')
@apiResponse(message='console删除成功')
async def delete(consoleId: int):
    """
    删除数据库连接
    :param consoleId:
    :return:
    """
    count = consoleService.delete(consoleId)
    return count


@router.get("")
@apiResponse(ConsoleIn)
async def getConsole(consoleId: int):
    """
    获取指定ID的角色信息
    :param consoleId:
    :return:
    """
    return consoleService.getOne(consoleId)


@router.put("/execute")
@apiResponse(ConsoleExecuteIn)
async def executeConsole(console: ConsoleExecuteIn):
    """
    执行控制台查询
    :param console:
    :return:
    """
    c: Console = consoleService.getOne(console.consoleId)
    if c is None:
        raise ApiException('控制台信息不存在')
    conn: Connect = connectService.getConnect(c.connectId)
    if conn is None:
        raise ApiException('控制台使用的数据连接不存在')

    dbpool = Dbpool(conn.drive, conn.connectStr, conn.username, conn.password)
    cursor = dbpool.fetch_cursor(console.content)
    i = 0
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        i += 1

    print(console.content)

    # for i in range(10000):
    # response.



