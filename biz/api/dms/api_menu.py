from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.model.dms import Menu
from biz.service.dms import menuService
from common import entityUtils

router = APIRouter(prefix="/menu")


class MenuIn(BaseModel):
    menuId: Optional[int]
    parentId: int
    name: str
    path: Optional[str]
    icon: Optional[str]
    attribute: Optional[dict]
    validity: str
    sortNo: Optional[str]
    children: Optional[List]

    class Config:
        orm_mode = True


@router.get("/page_list")
@apiResponse(List[MenuIn])
async def getPageList(current: int, pageSize: int, parentId: int = 0, keyword: str = '', isDelete: bool = False):
    menu_list = menuService.getMenuPageList(current, pageSize, keyword=keyword,
                                                     parentId=parentId, validity=None, isDelete=isDelete)
    return menu_list


@router.get("/list")
@apiResponse(List[MenuIn])
async def getList(menuId: int = None, parentId: int = None, validity: int = None, limit: int = None, isTree: bool = True):
    menu_list = menuService.getMenuList(menuId=menuId, parentId=parentId, validity=validity, limit=limit, isTree=isTree)
    return menu_list


@router.put('')
@apiResponse(MenuIn, message='菜单{name}保存成功')
async def save(menu: MenuIn):
    if menu.menuId is None:
        u = Menu()
    else:
        u = menuService.getMenu(menuId=menu.menuId)
        if u is None:
            raise ApiException(message='菜单[%s]不存在，无法修改' % menu.code)

    entityUtils.copy(menu, u)
    menuService.save(u)
    return u


@router.put('/sort')
@apiResponse(MenuIn)
async def saveSortNo(menuId: int, sortNo: int):
    menu = menuService.getMenu(menuId)
    if menu is not None:
        menu.sortNo = sortNo
        menuService.save(menu)
    return menu

@router.delete('')
@apiResponse(message='菜单删除成功')
async def delete(menuId: int):
    count = menuService.delete(menuId)
    return count
