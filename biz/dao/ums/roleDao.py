from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.ums import Role


def save(role: Role, ignore_fields=[], ignore_none=True):
    with get_session_scope() as session:
        if role.roleId is None:
            session.add(role)
            return role
        r = session.query(Role).filter(Role.roleId == role.roleId).first()
        if r is None:
            raise ApiException('角色不存在')
        r.copy(role, ignore_fields, ignore_none)
        return r;


def delete(roleId: int):
    with get_session_scope() as session:
        return session.query(Role).filter(Role.roleId == roleId).delete()


def get_one(roleId: int):
    with get_session_scope() as session:
        r: Role = session.query(Role).filter(Role.roleId == roleId).first()
        return r


def getList(type: str):
    with get_session_scope() as session:
        return session.query(Role).filter(Role.type == type).all()


def getPageList(where: [], order_by: [], limit: int, offset: int):
    list1 = baseDao.get_page_list([Role], where, order_by=order_by, limit=limit, offset=offset)
    return list1
