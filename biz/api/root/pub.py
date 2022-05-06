from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel

from biz.api.decorator import apiResponse
from biz.api.dms.api_menu import MenuIn
from biz.service.dms import dictService, menuService
from biz.service.ums import companyService, ruleService

router = APIRouter(prefix="/pub")


class CompanyIn(BaseModel):
    companyId: Optional[int]
    code: str
    name: str
    shortName: str
    children: Optional[List['CompanyIn']]

    class Config:
        orm_mode = True


CompanyIn.update_forward_refs()


class DictIn(BaseModel):
    dictId: Optional[int]
    value: Optional[str]
    name: str
    path: str
    isFolder: bool
    validity: str
    children: Optional[List['DictIn']]

    class Config:
        orm_mode = True


DictIn.update_forward_refs()


@router.get("/company_list")
@apiResponse(List[CompanyIn])
async def getCompanyList(parentId: int = 0):
    """
    获取子机构树
    :param parentId: 父机构ID
    :return:
    """
    company_list = companyService.getCompanyList(parentId=parentId, validity='valid', isDelete=False, isTree=True)
    return company_list


@router.get("/dict_tree")
@apiResponse(List[DictIn])
async def getDictTree(path: str, nodeType: str = 'node', validity: str = 'valid', isTop: bool = False):
    """
    获取字典树
    :param path: 路径
    :param nodeType: 获取类型，folder:目录，node:节点，不传则所有类型
    :param validity: 有效性：valid:有效，invalid:无效
    :param isTop: 是否仅获取下级子节点
    :return:
    """
    dict_tree = dictService.getChildTreeForPath(path=path, validity=validity, nodeType=nodeType, isTopDict=isTop)
    return dict_tree


@router.get("/menu_list")
@apiResponse(List[MenuIn])
async def getMenuList(uid: int = None):
    """
    获取菜单列表
    :param uid: 传入的用户ID
    :return:
    """
    main_menu_id = dictService.getDictByPath('/system/main_menu_id').value
    rule_list = ruleService.getRuleListByUserId(uid, ['front'])
    menu_list = menuService.getMenuList(parentId=[int(main_menu_id)], isTree=True,
                                        validity='valid', allow_rules=rule_list)
    return menu_list
