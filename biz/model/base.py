from typing import TypeVar, Generic, List, Optional

from pydantic.generics import GenericModel
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.orm import declared_attr
from common import stringUtils
from functools import wraps
from sqlalchemy import Column, Table


@declarative_mixin
class DefaultMixin:
    # 表名前缀
    __prefix__ = None
    # 表说明
    __comment__ = None
    # 建表参数
    __init_table_args__ = None

    # 默认自动按类生成数据库表名
    @declared_attr
    def __tablename__(self):
        if self.__prefix__ is None:
            return stringUtils.hump_to_underline(self.__name__)
        return '%s_%s' % (self.__prefix__, stringUtils.hump_to_underline(self.__name__))

    # 创建表的参数
    @declared_attr
    def __table_args__(self):
        default = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'comment': self.__comment__
        }
        default.update(self.__init_table_args__ if self.__init_table_args__ is not None else {})
        return default

    def copy(self, source: object, ignore_fields: list = [], ignore_none: bool = True):
        """
        复制一个对象的值给本实例
        :param source: 源对象
        :param ignore_none_value: 是否忽略源对象中的空值字段
        :param ignore_fields: 忽略的字段名列表
        :return:
        """
        if isinstance(source, self.__class__):
            for key in self.__dict__:
                # print('%s:' % key, end='')
                if key.startswith('_') or (ignore_fields is not None and key in ignore_fields):
                    # print('ignore field')
                    continue
                value = getattr(source, key)
                if value is None and ignore_none:
                    # print('ignore none')
                    continue
                setattr(self, key, value)
                # print('copy success')


T = TypeVar('T')  # 泛型类型 T


class PageList(GenericModel, Generic[T]):
    rows: Optional[List[T]]
    total: int
