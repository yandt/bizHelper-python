import os
from functools import wraps
from inspect import getframeinfo, stack
from typing import Optional, Union

from fastapi import Request, status
from fastapi.encoders import DictIntStrAny, SetIntStr, jsonable_encoder
from fastapi.routing import serialize_response
from fastapi.utils import create_response_field
from pydantic import BaseConfig
from pydantic.fields import ModelField

from biz.api.exceptions import ApiException
from biz.api.model import ResultModel
from biz.model.base import PageList


def apiResponse(response_model=None, code=200, message='',
                include_fields: Optional[Union[SetIntStr, DictIntStrAny]] = None,
                exclude_fields: Optional[Union[SetIntStr, DictIntStrAny]] = None,
                by_alias: bool = True,
                exclude_unset: bool = False,
                exclude_defaults: bool = False,
                exclude_none: bool = True,
                is_coroutine: bool = True,
                ):
    """
    标准的API返回体
    :param is_coroutine:
    :param exclude_none: 排除掉为Null的属性
    :param exclude_defaults: 排除掉为默认值的属性
    :param exclude_unset: 排除未设置的属性
    :param by_alias:
    :param exclude_fields: 排除的属性
    :param include_fields: 只返回指定的属性
    :param response_model: 返回类，用于校验实际返回是否正确，如空则不校验
    :param code: 返回状态代码
    :param message: 返回消息
    :return:
    """

    def wrapper(func):
        @wraps(func)
        async def _wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            if request is not None:
                path = request.url.path
                raise ApiException(code=status.HTTP_405_METHOD_NOT_ALLOWED, message='无权执行当前操作')
            data = await func(*args, **kwargs)
            total = None
            if isinstance(data, PageList):
                total = data.total
                data = data.rows
            response_name = "Response_%s_%s_%s_result_wrapper" % (
                __name__,
                func.__name__,
                response_model.__name__ if response_model is not None else 'none_model')
            if response_model is None:
                data = jsonable_encoder(
                    data,
                    include=include_fields,
                    exclude=exclude_fields,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            else:
                response_field = create_response_field(name=response_name, type_=response_model)
                data = await serialize_response(field=response_field, response_content=data,
                                                include=include_fields,
                                                exclude=exclude_fields,
                                                by_alias=by_alias,
                                                exclude_unset=exclude_unset,
                                                exclude_defaults=exclude_defaults,
                                                exclude_none=exclude_none,
                                                is_coroutine=is_coroutine
                                                )
            errmsg = message
            if isinstance(data, dict):
                errmsg = errmsg.format(**data)
            data = ResultModel(data=data, errorCode=code, errorMessage=errmsg, total=total)
            return data

        return _wrapper

    return wrapper
