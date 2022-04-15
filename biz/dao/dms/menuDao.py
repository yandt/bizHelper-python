import datetime

from sqlalchemy import or_, text, func
from sqlalchemy.orm import with_expression

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.dms import Menu


def save(menu: Menu, ignore_fields=[], ignore_none=True) -> Menu:
    with get_session_scope() as session:
        if menu.menuId is None:
            session.add(menu)
        else:
            c: Menu = session.query(Menu).filter(Menu.menuId == menu.menuId).first()
            if c is None:
                raise ApiException('菜单不存在')
            child_list = getChildList([c.menuId])
            child_ids = [c.menuId for c in child_list]
            if menu.parentId in child_ids:
                raise ApiException('上级菜单不允许为本级或下级')
            c.copy(menu, ignore_fields, ignore_none)
            c.modifyTime = datetime.datetime.now()
            return c


def delete(menuId: int) -> int:
    with get_session_scope() as session:
        children_count = session.query(Menu).filter(Menu.parentId == menuId).count()
        if children_count > 0:
            raise ApiException('该菜单包含子菜单，无法被删除')
        return session.query(Menu).filter(Menu.menuId == menuId).delete()


def get_one(menuId: int = None) -> Menu:
    with get_session_scope() as session:
        q = session.query(Menu).filter(Menu.menuId == menuId)
    com = q.first()
    if com is None:
        return None
    return com


def getPageList(where: [], order_by: [], limit: int, offset: int):
    pagelist = baseDao.get_page_list([Menu], where, order_by=order_by, limit=limit, offset=offset)
    return pagelist


def getList(where: [], order_by: [], limit: int = None):
    pagelist = baseDao.get_list([Menu], where, order_by=order_by)
    return pagelist


def getChildList(menuIds: list[int] = [], parentIds: list[int] = [], validity: str = None) -> list:
    sql = """  
        with recursive cte as 
         ( 
         select a.*, 0 as loclevel from dms_menu a where (a."menuId" = any(:MENU_IDS) or a."parentId" = any(:PARENT_IDS)) 
         union all  
         select k.*, loclevel + 1 as loclevel from dms_menu k inner join cte c on c."menuId" = k."parentId" 
         )
        select * from cte 
        where "menuId"*10000+"loclevel" in (select max("menuId"*10000+"loclevel") from cte group by "menuId")
        {validity_cont}
        order by "loclevel", "sortNo" desc
    """.format(
        validity_cont='and "validity" = :VALIDITY' if validity is not None else '',
    )
    with get_session_scope() as session:
        res = session.query(Menu).from_statement(text(sql)).params(
            MENU_IDS=menuIds, PARENT_IDS=parentIds, VALIDITY=validity).options(
            with_expression(Menu.loclevel, func.count().label('loclevel')))

    return res.all()
