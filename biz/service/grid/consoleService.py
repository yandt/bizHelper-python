from typing import List

from sqlalchemy import desc

from biz.dao.grid import consoleDao
from biz.model.base import PageList
from biz.model.grid import Console


def save(console: Console):
    return consoleDao.save(console)


def delete(consoleId: int):
    return consoleDao.delete(consoleId)


def getOne(consoleId: int):
    return consoleDao.get_one(consoleId)


def getList(createUid: int, validity: str = None):
    return consoleDao.getList(createUid, validity)


def createConsoleTree(list: List[Console], parentId: int = None):
    tmp_list = []
    for con in list:
        if con.loclevel == 0 and parentId is None:
            con.children = createConsoleTree(list, con.consoleId)
            tmp_list.append(con)
        elif con.parentId == parentId:
            con.children = createConsoleTree(list, con.consoleId)
            tmp_list.append(con)

    return tmp_list if len(tmp_list) > 0 else None


def getTree(createUid: int, validity: str = None):
    console_list = consoleDao.getChildList(createUid, parentIds=[0], validity=validity)
    return createConsoleTree(console_list)


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
        where.append(Console.name.like(keyword_like))

    pagelist = consoleDao.getPageList(createUid, where, [desc(Console.insertTime)], limit=limit, offset=offset)

    return pagelist


