from types import FunctionType, MethodType

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from biz.api.model import ErrorModel


def buildExceptionJSONResponse(code: int, exc: Exception):
    message = exc.__dict__.get('message', 'Message is null')
    error_name = exc.__class__.__name__
    show_type = 1
    if isinstance(exc, HTTPException):
        message = exc.detail
        data = {}
        show_type = 2
    elif isinstance(exc, RequestValidationError):
        data = {
            'body': exc.body,
            'errors': exc.errors()
        }
    elif isinstance(exc, ApiException):
        if exc.isBizError:
            error_name = 'BizError'
        show_type = exc.showType
        data = {}
    elif isinstance(exc, IntegrityError):
        show_type = 4
        message = '因数据问题，提交失败'
        data = {
            'detail': exc.detail
        }
    else:
        data = {}

    return JSONResponse(
        status_code=code,
        content=ErrorModel(errorCode=code,
                           name=error_name,
                           errorMessage=message,
                           data=jsonable_encoder(data),
                           showType=show_type
                           ).dict()
    )


def register_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return buildExceptionJSONResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_request_validation_handler(request: Request, exc: RequestValidationError):
        return buildExceptionJSONResponse(status.HTTP_422_UNPROCESSABLE_ENTITY, exc)

    @app.exception_handler(HTTPException)
    async def validation_http_exception_handler(request: Request, exc: HTTPException):
        return buildExceptionJSONResponse(exc.status_code, exc)

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException):
        return buildExceptionJSONResponse(exc.code, exc)


class ApiException(Exception):
    def __init__(self, message: str, code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 isBizError: bool = True, showType: int = 2):
        self.message = message
        self.code = code
        self.isBizError = isBizError
        self.showType = showType
