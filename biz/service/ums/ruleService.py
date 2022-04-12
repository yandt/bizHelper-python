from operator import or_

from sqlalchemy import asc

from biz.dao.ums import ruleDao
from biz.model.base import PageList
from biz.model.ums import Rule


def save(rule: Rule):
    return ruleDao.save(rule)


def delete(ruleId: int):
    return ruleDao.delete(ruleId)


def getRule(ruleId: int):
    return ruleDao.get_one(ruleId)


def getList(type: str = None):
    return ruleDao.getList(type)


def getPageList(pageno: int = 0,
                size: int = 10,
                keyword: str = '',
                ) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = [Rule.type == 'defined']

    if len(keyword) > 0:
        where.append(or_(Rule.name.like(keyword_like), Rule.path.like(keyword_like)))

    pagelist = ruleDao.getPageList(where, [asc(Rule.path)], limit=limit, offset=offset)

    return pagelist
