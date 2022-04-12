import datetime
from typing import List

from sqlalchemy import or_, text, func
from sqlalchemy.orm import with_expression, Session

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.dms import Dict


def resetDictPath(session: Session, save_dict: Dict, children_dict_list: List[Dict], parent_dict: Dict = None):
    # 按路径深度排序
    def dict_path_depth(elem):
        return elem.path.count('/')

    if parent_dict is None:
        children_dict_list.sort(key=dict_path_depth)

    if save_dict.parentId == 0:
        save_dict.path = '/' + save_dict.name
    else:
        if parent_dict is None:
            parent_dict = session.query(Dict).filter(Dict.dictId == save_dict.parentId).first()
            if parent_dict is None:
                raise ApiException('父节点不存在')
        save_dict.path = '%s/%s' % (parent_dict.path, save_dict.name)
    if save_dict.isFolder:
        for dd in children_dict_list:
            # 子列表中的当前字典忽略
            if dd.dictId == save_dict.dictId:
                continue
            # 直接子字典，则修改path
            if dd.parentId == save_dict.dictId:
                resetDictPath(session, dd, children_dict_list, save_dict)


def save(ddict: Dict, ignore_fields=[], ignore_none=True) -> Dict:
    with get_session_scope() as session:
        if ddict.dictId is None:
            resetDictPath(session, ddict, [])
            session.add(ddict)
        else:
            c: Dict = session.query(Dict).filter(Dict.dictId == ddict.dictId).first()
            if c is None:
                raise ApiException('节点不存在')
            child_list = getChildList(dictIds=[c.dictId], session=session)
            child_ids = [c.dictId for c in child_list]
            if ddict.parentId in child_ids:
                raise ApiException('上级节点不允许为本级或下级')
            c.copy(ddict, ignore_fields, ignore_none)
            resetDictPath(session, c, child_list)
            return c


def delete(dictId: int) -> int:
    with get_session_scope() as session:
        children_count = session.query(Dict).filter(Dict.parentId == dictId).count()
        if children_count > 0:
            raise ApiException('包含子节点，无法被删除')
        c: Dict = session.query(Dict).filter(Dict.dictId == dictId)
        return c.delete()
    return 0


def get_one(dictId: int = None, path: str = None) -> Dict:
    with get_session_scope() as session:
        q = session.query(Dict).filter(
            or_(
                Dict.dictId == dictId if dictId is not None else False,
                Dict.path == path if path is not None else False
            )
        )
    com = q.first()
    return com


def getPageList(where: [], order_by: [], limit: int, offset: int):
    pagelist = baseDao.get_page_list([Dict], where, order_by=order_by, limit=limit, offset=offset)
    return pagelist


def getList(where: [], order_by: []):
    return baseDao.get_list([Dict], where, order_by=order_by)


def getParentList(dictId: int, session: Session = None) -> list:
    sql = """
        with recursive cte as 
         ( 
         select a.*, 0 as loclevel from dms_dict a where a."dictId" = :DICT_ID
         union all  
         select k.*, loclevel + 1 as loclevel from dms_dict k join cte c on c."parentId" = k."dictId" 
         )
        select * from cte 
        where "dictId"||':'||"loclevel" in (select max("dictId"||':'||"loclevel") from cte group by "dictId")
        order by "loclevel" desc
    """

    def getQuery(s: Session):
        return s.query(Dict).from_statement(text(sql)).params(
            DICT_ID=dictId).options(
            with_expression(Dict.loclevel, func.count().label('loclevel')))

    # 没有传入会话时，创建一个会话
    if session is None:
        with get_session_scope() as session:
            q = getQuery(session)
        return q.all()
    # 使用传入的会话
    return getQuery(session).all()


def getChildList(dictIds: list[int] = [], parentIds: list[int] = [], validity: str = None,
                 session: Session = None) -> List[Dict]:
    sql = """  
        with recursive cte as 
         ( 
         select a.*, 0 as loclevel from dms_dict a where (a."dictId" = any(:DICT_IDS) or a."parentId" = any(:PARENT_IDS)) 
         union all  
         select k.*, loclevel + 1 as loclevel from dms_dict k inner join cte c on c."dictId" = k."parentId" 
         )
        select * from cte 
        where "dictId"||':'||"loclevel" in (select max("dictId"||':'||"loclevel") from cte group by "dictId")
        {validity_cont}
        order by "loclevel"
    """.format(
        validity_cont='and "validity" = :VALIDITY' if validity is not None else ''
    )

    def getQuery(s: Session):
        return s.query(Dict).from_statement(text(sql)).params(
            DICT_IDS=dictIds, PARENT_IDS=parentIds, VALIDITY=validity).options(
            with_expression(Dict.loclevel, func.count().label('loclevel')))

    # 没有传入会话时，创建一个会话
    if session is None:
        with get_session_scope() as session:
            q = getQuery(session)
        return q.all()
    # 使用传入的会话
    return getQuery(session).all()
