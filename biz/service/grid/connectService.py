from operator import or_

from sqlalchemy import asc, desc

from analyse.dbpool import Dbpool
from biz.api.exceptions import ApiException
from biz.dao.grid import connectDao
from biz.model.base import PageList
from biz.model.grid import Connect


def save(connect: Connect):
    return connectDao.save(connect)


def delete(connectId: int):
    return connectDao.delete(connectId)


def getConnect(connectId: int):
    return connectDao.get_one(connectId)


def getList(createUid: int, validity: str = None):
    return connectDao.getList(createUid, validity)


def getPageList(createUid: int,
                pageno: int = 0,
                size: int = 10,
                keyword: str = '',
                ) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = []

    if len(keyword) > 0:
        where.append(Connect.name.like(keyword_like))

    pagelist = connectDao.getPageList(createUid, where, [desc(Connect.insertTime)], limit=limit, offset=offset)

    return pagelist


def getDatabaseConnect(connectId: int):
    """
    根据数据连接ID，获取数据库连接
    :param connectId:
    :return:
    """
    conn = getConnect(connectId)
    if conn is None:
        raise ApiException('数据连接不存在')
    pool = Dbpool(conn.drive, conn.connectStr, conn.username, conn.password)
    return pool
