from fastapi import APIRouter
from biz.api.ums import api_user, api_company, api_rule, api_role

router = APIRouter(prefix="/ums")

router.include_router(api_user.router)
router.include_router(api_company.router)
router.include_router(api_rule.router)
router.include_router(api_role.router)

