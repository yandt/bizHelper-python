from sqlalchemy import asc, text, func
from sqlalchemy.orm import with_expression

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.ums import Rule, Role


def save(rule: Rule, ignore_fields=[], ignore_none=True):
    with get_session_scope() as session:
        if rule.ruleId is None:
            session.add(rule)
            return rule

        r = session.query(Rule).filter(Rule.ruleId == rule.ruleId).first()
        if r is None:
            raise ApiException('权限不存在')
        r.copy(rule, ignore_fields, ignore_none)
        return r


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


def getFrontRuleListByUserId(uid: int):
    sql = """
        with t1 as (
            select json_array_elements_text("attribute"->'functionRoles')::integer as roleid
            from ums_user
            where "uid" = :USERID
        ), t2 as (	
            select json_array_elements_text(attribute->'rules')::integer as ruleid, 1 as has_rule
            from ums_role 
            join t1 on "roleId" = t1."roleid"
        )
        select r."ruleId", r.path, r.type, t2.has_rule
        from ums_rule r 
        left join t2 on r."ruleId" = t2."ruleid" 
        where type =  any(:TYPELIST)
          and validity = 'valid'
    """

    with get_session_scope() as session:
        res = session.query(Rule).from_statement(text(sql)).params(
            USERID=uid, TYPELIST=['front', 'defined', 'back']).options(
            with_expression(Rule.hasRule, func.count().label('has_rule')))

    return res.all()


