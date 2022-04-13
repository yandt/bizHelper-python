from operator import or_

from sqlalchemy import asc, desc

from biz.dao.ums import roleDao
from biz.model.base import PageList
from biz.model.ums import Role


def save(role: Role):
    return roleDao.save(role)


def delete(roleId: int):
    return roleDao.delete(roleId)


def getRole(roleId: int):
    return roleDao.get_one(roleId)


def getList(type: str, validity: str = None):
    return roleDao.getList(type, validity)


def getPageList(pageno: int = 0,
                size: int = 10,
                keyword: str = '',
                type: str = 'function',
                ) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = [Role.type == type]

    if len(keyword) > 0:
        where.append(Role.name.like(keyword_like))

    pagelist = roleDao.getPageList(where, [desc(Role.insertTime)], limit=limit, offset=offset)

    return pagelist


