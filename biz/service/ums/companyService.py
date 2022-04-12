from typing import List

from sqlalchemy import or_, desc, asc

from biz.dao.ums import companyDao
from biz.model.base import PageList
from biz.model.ums import Company


def save(company: Company):
    """
    保存用户实例
    :param company: 实例
    :return:
    """
    companyDao.save(company)


def delete(uid: int) -> int:
    return companyDao.delete(uid)


def getCompany(companyId: int = None, code: str = None) -> Company:
    u = companyDao.get_one(companyId, code)
    return u


def createCompanyTree(list: List[Company], parentId: int = None):
    tmp_list = []
    for com in list:
        if com.loclevel == 0 and parentId is None:
            com.children = createCompanyTree(list, com.companyId)
            tmp_list.append(com)
        elif com.parentId == parentId:
            com.children = createCompanyTree(list, com.companyId)
            tmp_list.append(com)

    return tmp_list if len(tmp_list)>0 else None


def getCompanyPageList(pageno: int = 0,
                       size: int = 10,
                       parentId: int = 0,
                       keyword: str = '',
                       validity: str = None,
                       isDelete: int = 0,
                       isTree: bool = True) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = []

    if len(keyword) > 0:
        where.append(or_(Company.name.like(keyword_like), Company.code.like(keyword_like)))
    else:
        where.append(Company.parentId == parentId)
    if validity is not None:
        where.append(Company.validity == validity)
    where.append(Company.isDelete == isDelete)

    pagelist = companyDao.getPageList(where, limit=limit, offset=offset, order_by=[asc(Company.code)])

    if isTree:
        ids = [c.companyId for c in pagelist.rows]
        lclist = companyDao.getChildList(ids)
        pagelist.rows = createCompanyTree(lclist)

    return pagelist


def getCompanyList(parentId: int = 0,
                   validity: int = 1,
                   isDelete: int = 0,
                   isTree: bool = True) -> List[Company]:

    if not isTree:
        where = [Company.parentId == parentId]
        if validity is not None:
            where.append(Company.validity == validity)
        where.append(Company.isDelete == isDelete)
        list1 = companyDao.getList(where, order_by=[asc(Company.code)])
        return list1
    else:
        return createCompanyTree(companyDao.getChildList(parentIds=[parentId], validity=validity, isDelete=isDelete))
