from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.model.dms import Dict
from biz.service.dms import dictService
from common import entityUtils

router = APIRouter(prefix="/dict")


class DictIn(BaseModel):
    dictId: Optional[int]
    parentId: int
    name: str
    value: Optional[str]
    isFolder: Optional[int]
    attribute: Optional[dict]
    validity: Optional[str]
    path: Optional[str]
    children: Optional[List]

    class Config:
        orm_mode = True


@router.get("/page_list")
@apiResponse(List[DictIn])
async def getPageList(current: int, pageSize: int, parentId: int = 0, keyword: str = ''):
    """
    获取字典页列表
    :param current: 当前页
    :param pageSize: 页大小
    :param parentId: 上级ID
    :param keyword: 搜索关键字
    :return:
    """
    dict_list = dictService.getDictPageList(current, pageSize, keyword=keyword,
                                            parentId=parentId, validity=None)
    return dict_list


@router.get("/list")
@apiResponse(List[DictIn])
async def getList(parentId: int = 0, validity: int = None):
    """
    获取字典列表
    :param parentId: 上级ID
    :param validity: 有效性：valid:有效，invalid:无效
    :return:
    """
    dict_list = dictService.getDictList(parentId=parentId, validity=validity, isTree=True)
    return dict_list


@router.get("/parent_list")
@apiResponse(List[DictIn])
async def getParentList(dictId: int = 0):
    """
    获取所有上级字典列表
    :param dictId: 字典ID
    :return:
    """
    dict_list = dictService.getDictParentList(dictId=dictId)
    return dict_list


@router.get("/tree")
@apiResponse(List[DictIn])
async def getDictTree(path: str = '/', onlyNode: bool = True, validity: str = 'valid'):
    """
    获取字典树
    :param path: 路径
    :param onlyNode: 是否仅获取节点
    :param validity: 有效性
    :return:
    """
    return dictService.getChildTreeForPath(path, onlyNode, validity)


@router.put('')
@apiResponse(DictIn, message='节点[{name}]保存成功')
async def save(ddict: DictIn):
    """
    保存字典
    :param ddict: 字典数据
    :return:
    """
    if ddict.dictId is None:
        u = Dict()
    else:
        u = dictService.getDict(dictId=ddict.dictId)
        if u is None:
            raise ApiException(message='节点[%s]不存在，无法修改' % ddict.name)

    entityUtils.copy(ddict, u)
    dictService.save(u)
    return u


@router.delete('')
@apiResponse(message='节点删除成功')
async def delete(dictId: int):
    """
    删除节点
    :param dictId: 节点ID
    :return:
    """
    count = dictService.delete(dictId)
    return count
