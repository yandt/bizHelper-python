from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, JSON, Index, Table
from sqlalchemy.orm import query_expression

from biz.model.base import DefaultMixin

# 创建基类
BASE = declarative_base()


class DmsMixin(DefaultMixin):
    """
    基础数据系统表前缀
    """
    __prefix__ = 'dms'


class Dict(DmsMixin, BASE):
    """
    字典类
    """
    __comment__ = '字典类'
    dictId: int = Column(Integer, primary_key=True, comment='字典唯一ID')
    parentId: int = Column(Integer, comment='上级ID', nullable=False, server_default="0", index=True)
    path: str = Column(String, comment='归属路径', nullable=False, index=True)
    name: str = Column(String(50), comment='名称', nullable=False)
    value: str = Column(String(100), unique=True, comment='节点值', index=True)
    isFolder: int = Column(Integer, comment='是否为文件夹：0节点，1文件夹', index=True, default=0, nullable=False)
    validity: str = Column(String, comment='有效性：invalid无效，valid有效', index=True, default='valid', nullable=False)
    attribute: dict = Column(JSON, comment='节点属性', default={}, server_default="{}")
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())

    # 查询时表达式，仅查询时赋值
    loclevel: int = query_expression()

    __table_args__ = (Index('dict_parent_id_name', 'parentId', 'name'),)


class Menu(DmsMixin, BASE):
    """
    字典类
    """
    __comment__ = '系统菜单'
    menuId: int = Column(Integer, primary_key=True, comment='菜单唯一ID')
    parentId: int = Column(Integer, comment='上级菜单ID', nullable=False, server_default="0", index=True)
    name: str = Column(String(50), comment='名称', nullable=False)
    path: str = Column(String, comment='菜单路径')
    icon: str = Column(String(100), unique=True, comment='图标', index=True)
    validity: str = Column(String(20), comment='有效性：invalid无效，valid有效', index=True, default='valid', nullable=False)
    attribute: dict = Column(JSON, comment='节点属性', default={}, server_default="{}")
    sortNo: int = Column(Integer, comment='排序编号', default=0, server_default="0")
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())

    # 查询时表达式，仅查询时赋值
    loclevel: int = query_expression()


def init_db(engine, tables=None, checkfirst=True):
    """
    初始化表
    :param checkfirst:
    :param tables:
    :param engine: 数据库引擎
    :return:
    """
    BASE.metadata.create_all(engine, tables, checkfirst)


def drop_db(engine, tables=None, checkfirst=True):  #
    """
    删除表
    :param tables:
    :param checkfirst:
    :param engine: 数据库引擎
    :return:
    """
    BASE.metadata.drop_all(engine, tables, checkfirst)
