from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.api.exceptions import ApiException
from biz.model.ums import Company
from biz.service.ums import companyService
from common import entityUtils

router = APIRouter(prefix="/company")


class CompanyIn(BaseModel):
    companyId: Optional[int]
    parentId: int
    code: str
    name: str
    shortName: str
    attribute: Optional[dict]
    validity: str
    children: Optional[List]

    class Config:
        orm_mode = True


@router.get("/page_list")
@apiResponse(List[CompanyIn])
async def getPageList(current: int, pageSize: int, parentId: int = 0, keyword: str = '', isDelete: bool = False):
    company_list = companyService.getCompanyPageList(current, pageSize, keyword=keyword,
                                                     parentId=parentId, validity=None, isDelete=isDelete)
    return company_list


@router.get("/list")
@apiResponse(List[CompanyIn])
async def getList(parentId: int = 0, validity: int = None, isDelete: bool = False):
    company_list = companyService.getCompanyList(parentId=parentId, validity=validity, isDelete=isDelete, isTree=True)
    return company_list


@router.put('')
@apiResponse(CompanyIn, message='部门{name}保存成功')
async def save(company: CompanyIn):
    if company.companyId is None:
        u = companyService.getCompany(code=company.code)
        if u is not None:
            raise ApiException(message='部门代码%s已存在，请改变' % company.code)
        u = Company()
    else:
        u = companyService.getCompany(companyId=company.companyId)
        if u is None or u.isDelete:
            raise ApiException(message='部门[%s]不存在，无法修改' % company.code)

    entityUtils.copy(company, u)
    companyService.save(u)
    return u


@router.delete('')
@apiResponse(message='部门删除成功')
async def delete(companyId: int):
    count = companyService.delete(companyId)
    return count
