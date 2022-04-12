import datetime

from sqlalchemy import or_, text, select, func
from sqlalchemy.orm import with_expression

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.ums import Company


def save(company: Company, ignore_fields=[], ignore_none=True) -> Company:
    with get_session_scope() as session:
        if company.companyId is None:
            session.add(company)
        else:
            c: Company = session.query(Company).filter(Company.companyId == company.companyId).first()
            if c is None or c.isDelete:
                raise ApiException('部门不存在')
            child_list = getChildList([c.companyId])
            child_ids = [c.companyId for c in child_list]
            if company.parentId in child_ids:
                raise ApiException('上级部门不允许为本级或下级')
            c.copy(company, ignore_fields, ignore_none)
            c.modifyTime = datetime.datetime.now()
            return c


def delete(companyId: int) -> int:
    with get_session_scope() as session:
        children_count = session.query(Company).filter(Company.parentId == companyId, not Company.isDelete).count()
        if children_count > 0:
            raise ApiException('该部门包含子部门，无法被删除')
        c: Company = session.query(Company).filter(Company.companyId == companyId).first()
        if c is None or c.isDelete:
            raise ApiException('部门不存在')
        else:
            c.isDelete = True
            c.modifyTime = datetime.datetime.now()
        return 1
    return 0


def get_one(companyId: int = None, code: str = None) -> Company:
    with get_session_scope() as session:
        q = session.query(Company).filter(
            or_(Company.companyId == companyId if companyId is not None else False,
                Company.code == code if code is not None else False
                ))
    com = q.first()
    if com is None or com.isDelete:
        return None
    return com


def getPageList(where: [], order_by: [], limit: int, offset: int):
    pagelist = baseDao.get_page_list([Company], where, order_by=order_by, limit=limit, offset=offset)
    return pagelist


def getList(where: [], order_by: []):
    pagelist = baseDao.get_list([Company], where, order_by=order_by)
    return pagelist


def getChildList(companyIds: list[int] = [], parentIds: list[int] = [], validity: str = None,
                 isDelete: bool = False) -> list:
    sql = """  
        with recursive cte as 
         ( 
         select a.*, 0 as loclevel from ums_company a where (a."companyId" = any(:COMPANY_IDS) or a."parentId" = any(:PARENT_IDS)) 
         union all  
         select k.*, loclevel + 1 as loclevel from ums_company k inner join cte c on c."companyId" = k."parentId" 
         )
        select * from cte 
        where "companyId"||':'||"loclevel" in (select max("companyId"||':'||"loclevel") from cte group by "companyId")
        {validity_cont} {isdelete_cont} 
        order by "loclevel", "code"
    """.format(
        validity_cont='and "validity" = :VALIDITY' if validity is not None else '',
        isdelete_cont='and "isDelete" = :ISDELETE' if isDelete is not None else ''
    )
    with get_session_scope() as session:
        res = session.query(Company).from_statement(text(sql)).params(
            COMPANY_IDS=companyIds, PARENT_IDS=parentIds, VALIDITY=validity, ISDELETE=isDelete).options(
            with_expression(Company.loclevel, func.count().label('loclevel')))

    return res.all()

# cl = getChildList([1, 2])
# print(cl)
