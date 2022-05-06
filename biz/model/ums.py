from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, func, Boolean, Index, ARRAY
from sqlalchemy.orm import relationship, query_expression

from biz.model.base import DefaultMixin

# 创建基类
BASE = declarative_base()


class UmsMixin(DefaultMixin):
    """
    用户系统表前缀
    """
    __prefix__ = 'ums'


class User(BASE, UmsMixin):
    """
    用户主类
    """
    __comment__ = '用户主类'
    # 用户唯一ID
    uid: int = Column(Integer, primary_key=True, comment='用户唯一ID')
    nick: str = Column(String(50), unique=True, comment='用户昵称', nullable=False)
    name: str = Column(String(50), comment='用户姓名', nullable=False, index=True)
    email: str = Column(String(50), comment='注册邮箱', index=True)
    mobile: str = Column(String(50), comment='注册手机号', index=True)
    avatar: str = Column(String(255), comment='头像地址')
    password: str = Column(String(200), comment='用户密码')
    passwordTime: datetime = Column(DateTime, comment='密码变化时间')
    companyId: int = Column(Integer, ForeignKey('ums_company.companyId'), comment='归属部门ID', index=True)
    attribute: dict = Column(JSON, comment='用户属性', default={}, )
    validity: int = Column(String(50), comment='状态:invalid无效，valid有效', index=True)
    isDelete: bool = Column(Boolean, server_default='0', default=False, nullable=False, comment='是否已删除', index=True)
    insertTime: datetime = Column(DateTime, default=func.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())

    # 用户归属机构
    company = relationship('Company', uselist=False, lazy='joined')


class Company(BASE, UmsMixin):
    """
    部门
    """
    companyId: int = Column(Integer, primary_key=True, comment='部门ID', nullable=False)
    parentId: int = Column(Integer, comment='上级部门ID', nullable=False, index=True, server_default="0")
    code: str = Column(String(50), unique=True, comment='部门代码')
    name: str = Column(String(50), comment='部门名称', nullable=False)
    shortName: str = Column(String(50), comment='部门名称简写')
    validity: str = Column(String(50), comment='状态:invalid无效，valid有效', index=True, default='valid',
                           server_default='valid')
    attribute: dict = Column(JSON, comment='部门属性', default={})
    isDelete: bool = Column(Boolean, server_default='0', default=False, nullable=False, comment='是否已删除')
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())

    # 查询时表达式，仅查询时赋值
    loclevel: int = query_expression()


class Rule(BASE, UmsMixin):
    """
    权限
    """
    ruleId: int = Column(Integer, primary_key=True, comment='权限ID', nullable=False)
    name: str = Column(String(50), nullable=True, comment='权限名称')
    path: str = Column(String(300), nullable=True, comment='权限路径', unique=True)
    type: str = Column(String(10),nullable=True, comment='权限类型（front:前端,back:后端,defined:自定义）')
    validity: str = Column(String(50), comment='状态:invalid无效，valid有效', index=True, default='valid',
                           server_default='valid')
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())
    # 查询时表达式，仅查询时赋值
    hasRule: int = query_expression()


class Role(BASE, UmsMixin):
    """
    角色
    """
    roleId: int = Column(Integer, primary_key=True, comment='角色ID', nullable=False)
    name: str = Column(String(50), nullable=True, comment='角色名称')
    type: str = Column(String(10),nullable=True, comment='角色类型（data:数据,function:功能）')
    attribute: dict = Column(JSON, comment='角色属性', default={}, server_default='{}')
    validity: str = Column(String(50), comment='状态:invalid无效，valid有效', index=True, default='valid',
                           server_default='valid')
    insertTime: datetime = Column(DateTime, default=datetime.now(), comment='新增时间', nullable=False)
    modifyTime: datetime = Column(DateTime, comment='修改时间', onupdate=datetime.now())


