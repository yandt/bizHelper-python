from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, query_expression
from biz.model.base import DefaultMixin

# 创建基类
BASE = declarative_base()


class GridMixin(DefaultMixin):
    """
    Grid系统表前缀
    """
    __prefix__ = 'grid'


class Connect(GridMixin, BASE):
    """
    数据连接
    """
    __comment__ = '数据连接'

    connectId: int = Column(Integer, primary_key=True, comment='数据连接唯一ID')
    name: str = Column(String(50), nullable=False, comment='连接名称')
    drive: str = Column(String(50), index=True, nullable=False, comment='连接驱动')
    connectStr: str = Column(String, nullable=False, comment='连接字符串')
    username: str = Column(String(200), nullable=False, comment='用户名')
    password: str = Column(String(200), comment='密码')
    createUid: int = Column(Integer, index=True, nullable=False, comment='创建者ID')
    visibility: str = Column(String(20), index=True, nullable=False, comment='可见性：public公开，private私有')
    validity: str = Column(String(20), comment='有效性：invalid无效，valid有效', index=True, default='valid', nullable=False)
    attribute: dict = Column(JSON, comment='连接属性', default={}, server_default="{}")
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())


class Console(GridMixin, BASE):
    """
    控制台
    """
    consoleId: int = Column(Integer, primary_key=True, comment='控制台唯一ID')
    connectId: int = Column(Integer, ForeignKey('grid_connect.connectId'), comment='数据连接ID', index=True)
    parentId: int = Column(Integer, nullable=False, comment='上级ID')
    name: str = Column(String(50), nullable=False, comment='控制台名称')
    tableName: str = Column(String, comment='当前数据库名')
    content: str = Column(Text, comment='控制台内容')
    comment: str = Column(Text, comment='备注内容')
    isFolder: int = Column(Integer, comment='是否为文件夹：0节点，1文件夹', index=True, default=0, nullable=False)
    createUid: int = Column(Integer, index=True, nullable=False, comment='创建者ID')
    attribute: dict = Column(JSON, comment='连接属性', default={}, server_default="{}")
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())
    sortNo: int = Column(Integer, comment='排序编号', default=0, server_default="0")

    # 查询时表达式，仅查询时赋值
    loclevel: int = query_expression()



