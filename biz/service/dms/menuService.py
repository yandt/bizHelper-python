from typing import List

from sqlalchemy import or_, asc, desc

from biz.dao.dms import menuDao
from biz.model.base import PageList
from biz.model.dms import Menu
from biz.model.ums import Rule
from common import pathUtils


def save(menu: Menu):
    """
    保存用户实例
    :param menu: 实例
    :return:
    """
    menuDao.save(menu)


def delete(uid: int) -> int:
    return menuDao.delete(uid)


def getMenu(menuId: int = None) -> Menu:
    u = menuDao.get_one(menuId)
    return u


def createMenuTree(list: List[Menu], parentId: int = None):
    tmp_list = []
    for com in list:
        if com.loclevel == 0 and parentId is None:
            com.children = createMenuTree(list, com.menuId)
            tmp_list.append(com)
        elif com.parentId == parentId:
            com.children = createMenuTree(list, com.menuId)
            tmp_list.append(com)

    return tmp_list if len(tmp_list) > 0 else None


def getMenuPageList(pageno: int = 0,
                    size: int = 10,
                    parentId: int = 0,
                    keyword: str = '',
                    validity: str = None,
                    isDelete: int = 0,
                    isTree: bool = True) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = []

    if len(keyword) > 0:
        where.append(or_(Menu.name.like(keyword_like), Menu.code.like(keyword_like)))
    else:
        where.append(Menu.parentId == parentId)
    if validity is not None:
        where.append(Menu.validity == validity)
    where.append(Menu.isDelete == isDelete)

    pagelist = menuDao.getPageList(where, limit=limit, offset=offset, order_by=[asc(Menu.code)])

    if isTree:
        ids = [c.menuId for c in pagelist.rows]
        lclist = menuDao.getChildList(ids)
        pagelist.rows = createMenuTree(lclist)

    return pagelist


def filterAllowMenus(menu_list: list[Menu], rule_list: list[Rule]):
    """
    过滤出有权限的菜单
    :param menu_list: 菜单列表
    :param rule_list: 权限列表
    :return:
    """
    new_menus = []
    if rule_list is None:
        return menu_list
    rule_list = sorted(rule_list, key=lambda d: d.path.count('/'), reverse=True)
    for menu in menu_list:
        menu_pass = True
        if menu.path is not None and len(menu.path) > 0:
            for rule in rule_list:
                if pathUtils.umiRoutesPathMatches(rule.path, menu.path):
                    if rule.hasRule == 1:
                        break;
                    if rule.hasRule == 0 or rule.hasRule is None:
                        menu_pass = False
        if menu_pass:
            new_menus.append(menu)
    return new_menus


def getMenuList(
        menuId: int = None,
        parentId: int = None,
        validity: int = None,
        isTree: bool = True,
        limit: int = None,
        allow_rules: list[Rule] = None
) -> List[Menu]:
    if not isTree:
        where = [Menu.parentId == parentId]
        if validity is not None:
            where.append(Menu.validity == validity)
        list1 = menuDao.getList(where, order_by=[desc(Menu.sortNo)], limit=limit)
        list1 = filterAllowMenus(list1, allow_rules)
        return list1
    else:
        list1 = menuDao.getChildList(menuIds=[menuId], parentIds=[parentId], validity=validity)
        list1 = filterAllowMenus(list1, allow_rules)
        return createMenuTree(list1)
