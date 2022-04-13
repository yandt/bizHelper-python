from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.class_validators import Optional

from biz.api.decorator import apiResponse
from biz.model.ums import Rule
from biz.service.ums import ruleService
from common import entityUtils

router = APIRouter(prefix="/rule")


class RuleIn(BaseModel):
    ruleId: Optional[int]
    name: str
    type: str
    path: str
    validity: str

    class Config:
        orm_mode = True


@router.get("/list")
@apiResponse(List[RuleIn])
async def getList(type: str = None):
    rule_list = ruleService.getList(type)
    return rule_list


@router.get("/defined_list")
@apiResponse(List[RuleIn])
async def getDefinedList(current: int, pageSize: int, keyword: str = '',):
    page_list = ruleService.getPageList(current, pageSize, keyword)
    return page_list


@router.put('')
@apiResponse(RuleIn, message='权限[ {name} ]保存成功')
async def save(rule: RuleIn):
    r = Rule()
    entityUtils.copy(rule, r)
    ruleService.save(r)
    return r


@router.delete('')
@apiResponse(message='权限解除成功')
async def delete(ruleId: int):
    count = ruleService.delete(ruleId)
    return count


