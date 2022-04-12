from sqlalchemy import asc

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.ums import Rule


def save(rule: Rule, ignore_fields=[], ignore_none=True):
    with get_session_scope() as session:
        if rule.ruleId is None:
            session.add(rule)
            return rule

        r = session.query(Rule).filter(Rule.ruleId == rule.ruleId).first()
        if r is None:
            raise ApiException('权限不存在')
        r.copy(rule, ignore_fields, ignore_none)
        return r;


def delete(ruleId: int):
    with get_session_scope() as session:
        return session.query(Rule).filter(Rule.ruleId == ruleId).delete()


def get_one(ruleId: int):
    with get_session_scope() as session:
        r: Rule = session.query(Rule).filter(Rule.ruleId == ruleId).first()
        return r


def getList(type: str = None):
    with get_session_scope() as session:
        return session.query(Rule).filter(Rule.type == type if type is not None else True).order_by(asc(Rule.name)).all()


def getPageList(where: [], order_by: [], limit: int, offset: int):
    list1 = baseDao.get_page_list([Rule], where, order_by=order_by, limit=limit, offset=offset)
    return list1