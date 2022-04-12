from typing import List

from sqlalchemy import or_, asc, desc

from biz.api.exceptions import ApiException
from biz.dao.dms import dictDao
from biz.model.base import PageList
from biz.model.dms import Dict


def save(dict: Dict):
    """
    保存用户实例
    :param dict: 实例
    :return:
    """
    dictDao.save(dict)


def delete(uid: int) -> int:
    return dictDao.delete(uid)


def getDict(dictId: int = None) -> Dict:
    u = dictDao.get_one(dictId)
    return u


def getDictByPath(path: str = None) -> Dict:
    u = dictDao.get_one(path=path)
    if u is None or u.validity == 'invalid':
        raise ApiException('未获取到[ %s ]的值，请联系系统管理员增加'%path)
    return u


def createDictTree(list: List[Dict], parentId: int = None):
    tmp_list = []
    for com in list:
        if com.loclevel == 0 and parentId is None:
            com.children = createDictTree(list, com.dictId)
            tmp_list.append(com)
        elif com.parentId == parentId:
            com.children = createDictTree(list, com.dictId)
            tmp_list.append(com)

    return tmp_list if len(tmp_list) > 0 else None


def getDictPageList(pageno: int = 0,
                    size: int = 10,
                    parentId: int = 0,
                    keyword: str = '',
                    validity: str = None,
                    isTree: bool = False) -> PageList:
    offset = (pageno - 1) * size
    limit = size
    keyword_like = '%%%s%%' % keyword
    where = []

    if len(keyword) > 0 and parentId == 0:
        where.append(or_(Dict.name.like(keyword_like), Dict.value.like(keyword_like)))
    else:
        where.append(Dict.parentId == parentId)
    if validity is not None:
        where.append(Dict.validity == validity)

    pagelist = dictDao.getPageList(where, limit=limit, offset=offset, order_by=[desc(Dict.isFolder), asc(Dict.name), ])

    if isTree:
        ids = [c.dictId for c in pagelist.rows]
        lc_list = dictDao.getChildList(ids)
        pagelist.rows = createDictTree(lc_list)

    return pagelist


def getDictList(parentId: int = 0,
                validity: int = 1,
                isTree: bool = True) -> List[Dict]:
    if not isTree:
        where = [Dict.parentId == parentId]
        if validity is not None:
            where.append(Dict.validity == validity)
        list1 = dictDao.getList(where, order_by=[asc(Dict.code)])
        return list1
    else:
        return createDictTree(dictDao.getChildList(parentIds=[parentId], validity=validity))


def getDictParentList(dictId: int):
    return dictDao.getParentList(dictId)


def createDictTree_adv(dict_list: list[Dict], parentId: int = None, isTopDict: bool = None):
    """
    纯靠parentid生成树
    :param isTopDict: 是否只含有顶层字典
    :param parentId: 上级ID
    :param dict_list: 字典列表
    :return:
    """

    def dict_path(elem):
        return elem.path

    if len(dict_list) == 0:
        return None
    tmp_list = []
    path_level = 999999  # 定义默认的路径级数
    if parentId is None:
        # 仅第一次进入时，按路径排序，路径排序靠前的是根节点
        dict_list.sort(key=dict_path)
        for d in dict_list:
            cur_level = d.path.count('/')
            if cur_level <= path_level:
                path_level = cur_level
                if not isTopDict:
                    d.children = createDictTree_adv(dict_list, d.dictId)
                tmp_list.append(d)
        return tmp_list

    for d in dict_list:
        if d.parentId == parentId:
            d.children = createDictTree_adv(dict_list, d.dictId)
            tmp_list.append(d)

    return tmp_list


def getChildTreeForPath(path: str, nodeType: str = None, validity: str = None, isTopDict: bool = None) -> list[Dict]:
    """
    获取子节点树
    :param path: 路径
    :param nodeType: 节点类型: node:节点，folder:目录，其他为两者均获取
    :param validity: valid:有效，invalid:无效
    :param isTopDict: 是否仅顶层
    :return:
    """
    where = [Dict.path.like(path + '%')]
    if validity is not None:
        where.append(Dict.validity == validity)
    if nodeType == 'node':
        where.append(Dict.isFolder == 0)
    elif nodeType == 'folder':
        where.append(Dict.isFolder == 1)

    pagelist = dictDao.getList(where, order_by=[asc(Dict.path), desc(Dict.isFolder), asc(Dict.name)])

    pagelist = createDictTree_adv(pagelist, isTopDict=isTopDict)

    return pagelist
