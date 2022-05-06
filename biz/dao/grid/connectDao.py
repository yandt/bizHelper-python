from sqlalchemy import or_

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope
from biz.dao import baseDao
from biz.model.grid import Connect


def save(connect: Connect, ignore_fields=[], ignore_none=True):
    with get_session_scope() as session:
        if connect.connectId is None:
            session.add(connect)
            return connect
        r = session.query(Connect).filter(Connect.connectId == connect.connectId).first()
        if r is None:
            raise ApiException('数据连接不存在')
        if r.createUid != connect.createUid:
            raise ApiException('不允许保存非本人创建的数据库连接')
        r.copy(connect, ignore_fields, ignore_none)
        return r


def delete(connectId: int):
    with get_session_scope() as session:
        return session.query(Connect).filter(Connect.connectId == connectId).delete()


def get_one(connectId: int):
    with get_session_scope() as session:
        r: Connect = session.query(Connect).filter(Connect.connectId == connectId).first()
        return r


def getList(createUid: int, validity: str = None):
    with get_session_scope() as session:
        return session.query(Connect).filter(
            Connect.validity == validity if validity is not None else True,
            or_(Connect.createUid == createUid, Connect.visibility == 'public')
        ).all()


def getPageList(createUid: int, where: [], order_by: [], limit: int, offset: int):
    www = [or_(Connect.createUid == createUid, Connect.visibility == 'public')]
    www.extend(where)
    list1 = baseDao.get_page_list([Connect], www, order_by=order_by, limit=limit, offset=offset)
    return list1
