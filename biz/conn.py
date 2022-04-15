from config import biz_db
from common.db.pool import Pool

from sqlalchemy.orm import Session, Query
from contextlib import contextmanager


def get_session() -> Session:
    return Pool().session


def get_engine():
    return Pool().gen_engine()


# 定义上下文函数，使能够自动进行事务处理，
# 定义上下文件函数的方法就是加上contextmanager装饰器
# 执行逻辑：在函数开始时建立数据库会话，此时会自动建立一个数据库事务；当发生异常时回滚（rollback）事务，当
# 退出时关闭(close)连接
@contextmanager
def get_session_scope() -> Session:
    # print('init session')
    session = get_session()
    try:
        yield session
        # print('commit')
        session.commit()
    except Exception as e:
        # print('session-rollback')
        session.rollback()
        raise e
    finally:
        # print('session-close')
        session.close()
