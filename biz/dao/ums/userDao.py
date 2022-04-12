import datetime

from biz.api.exceptions import ApiException
from biz.conn import get_session_scope, get_session
from biz.dao import baseDao
from biz.model.ums import User
from sqlalchemy import or_, and_

from biz.service.dms import dictService


def save(user: User, encrypt_password_func, password: str = None, ignore_fields=[], ignore_none=True):
    """
    保存用户信息
    :param user: 用户实例
    :param encrypt_password_func: 密码加密方法
    :param password: 如需修改密码，请传入此参数
    :param ignore_fields: 忽略保存的字段
    :param ignore_none: 忽略保存为空的字段
    :return: 返回修改后的用户实例
    """
    with get_session_scope() as session:
        if user.uid is None:
            # 获取密码加密
            if password is not None:
                user.password = encrypt_password_func(password)
                user.passwordTime = datetime.datetime.now()
            session.add(user)
            session.flush()
            user = session.query(User).filter(User.uid==user.uid).first()
            return user
        else:
            u: User = session.query(User).filter(User.uid == user.uid).first()
            if u is None or u.isDelete:
                raise ApiException('用户不存在')
            if u:
                ignore_fields.append('password_time')
                ignore_fields.append('company')
                ignore_fields.append('password')
                u.copy(user, ignore_fields=ignore_fields, ignore_none=ignore_none)
                u.modifyTime = datetime.datetime.now()
                # 修改密码
                if password is not None:
                    u.password = encrypt_password_func(password)
                    u.passwordTime = datetime.datetime.now()
            return u


def delete(uid: int) -> int:
    with get_session_scope() as session:
        u: User = session.query(User).filter(User.uid == uid).first()
        if u is None or u.isDelete:
            raise ApiException('用户不存在')
        admin_nick = dictService.getDictByPath('/system/user/admin_nick').value
        if u.nick == admin_nick:
            raise ApiException('这是系统管理员，不允许删除')
        else:
            u.isDelete = True
        return 1
    return 0


def get_one(uid: int = None, nick: str = None, email: str = None, mobile: str = None) -> User:
    with get_session_scope() as session:
        q = session.query(User).filter(
            or_(User.uid == uid if uid is not None else False,
                User.nick == nick if nick is not None else False,
                User.email == email if email is not None else False,
                User.mobile == mobile if mobile is not None else False
                ))
    user = q.first()
    if user is None or user.isDelete:
        return None
    return user


def getPageList(where: [], order_by: [], limit: int, offset: int):
    list1 = baseDao.get_page_list([User], where, order_by=order_by, limit=limit, offset=offset)
    return list1
