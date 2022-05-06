from sqlalchemy import or_, text, func
from sqlalchemy.orm import with_expression

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.grid import Console


def save(console: Console, ignore_fields=[], ignore_none=True):
    with get_session_scope() as session:
        if console.consoleId is None:
            session.add(console)
            return console
        r = session.query(Console).filter(Console.consoleId == console.consoleId).first()
        if r is None:
            raise ApiException('Console不存在')
        if r.createUid != console.createUid:
            raise ApiException('不允许修改非本人的Console')
        r.copy(console, ignore_fields, ignore_none)
        return r


def delete(consoleId: int):
    with get_session_scope() as session:
        return session.query(Console).filter(Console.consoleId == consoleId).delete()


def get_one(consoleId: int):
    with get_session_scope() as session:
        r: Console = session.query(Console).filter(Console.consoleId == consoleId).first()
        return r


def getList(createUid: int, validity: str = None):
    with get_session_scope() as session:
        return session.query(Console).filter(
            Console.validity == validity if validity is not None else True,
            Console.createUid == createUid
        ).all()


def getPageList(createUid: int, where: [], order_by: [], limit: int, offset: int):
    www = [Console.createUid == createUid]
    www.extend(where)
    list1 = baseDao.get_page_list([Console], www, order_by=order_by, limit=limit, offset=offset)
    return list1


def getChildList(createUid: int, consoleIds: list[int] = [], parentIds: list[int] = [], validity: str = None) -> list:
    sql = """  
        with recursive cte as 
         ( 
         select a.*, 0 as loclevel from grid_console a 
            where a."createUid" = :CREATE_UID and (a."consoleId" = any(:CONSOLE_IDS) or a."parentId" = any(:PARENT_IDS)) 
         union all  
         select k.*, loclevel + 1 as loclevel from grid_console k inner join cte c on c."consoleId" = k."parentId" 
            where k."createUid" = :CREATE_UID
         )
        select * from cte 
        where "consoleId"*10000+"loclevel" in (select max("consoleId"*10000+"loclevel") from cte group by "consoleId")
        {validity_cont}
        order by "loclevel", "sortNo" desc
    """.format(
        validity_cont='and "validity" = :VALIDITY' if validity is not None else '',
    )
    with get_session_scope() as session:
        res = session.query(Console).from_statement(text(sql)).params(CREATE_UID=createUid,
            CONSOLE_IDS=consoleIds, PARENT_IDS=parentIds, VALIDITY=validity).options(
            with_expression(Console.loclevel, func.count().label('loclevel')))

    return res.all()