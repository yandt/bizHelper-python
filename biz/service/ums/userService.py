import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy import or_, desc
from starlette import status

from biz.dao.ums import userDao
from biz.dao import baseDao
from biz.model.ums import User
from config import SECRET_KEY, ALGORITHM, TOKEN_URL

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 密码哈希
def get_password_hash(password):
    return pwd_context.hash(password)


# 校验密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def save(user: User, password: str = None):
    """
    保存用户实例
    :param password: 修改密码使用此参数
    :param user: 实例
    :return:
    """
    return userDao.save(user, get_password_hash, password=password)


def delete(uid: int) -> int:
    return userDao.delete(uid)


def getUser(uid: int = None, nick: str = None, email: str = None, mobile: str = None) -> User:
    u = userDao.get_one(uid, nick, email, mobile)
    return u


def getUserList(pageno: int = 0, size: int = 10, keyword: str = '', validity: str = None, isDelete: int = 0) -> list:
    offset = (pageno - 1) * size
    limit = size
    keyword = '%%%s%%' % keyword
    where = []

    if len(keyword) > 0:
        where.append(or_(User.name.like(keyword), User.nick.like(keyword)))
    if validity is not None:
        where.append(User.validity == validity)
    where.append(User.isDelete == isDelete)

    list1 = userDao.getPageList(where, limit=limit, offset=offset, order_by=[desc(User.insertTime)])
    return list1


def authenticate_user(user: User, plain_password: str):
    """
    校验用户密码是否正确
    :param user: 用户实例
    :param plain_password: 待校验明文密码
    :return:
    """
    if user is None:
        return False
    return verify_password(plain_password, user.password)


async def getCurrentUser(token: str = Depends(OAuth2PasswordBearer(tokenUrl=TOKEN_URL))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = getUser(nick=username)
    if user is None:
        raise credentials_exception
    return user
