from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')  # 泛型类型 T


class ResultModel(GenericModel, Generic[T]):
    success: bool = True
    errorCode: int = 0
    errorMessage: str = ''
    data: Optional[T]
    total: Optional[int]


class ErrorModel(BaseModel):
    success: bool = False
    name: str
    errorCode: int = 0
    errorMessage: str = ''
    data: Optional[object]
    showType: int = 2
