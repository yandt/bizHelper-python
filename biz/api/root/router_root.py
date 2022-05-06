from fastapi import APIRouter, Depends

from biz.api.decorator import apiResponse
from biz.api.grid import router_grid
from biz.api.root import token, pub
from biz.api.ums import router_ums
from biz.api.dms import router_dms

router = APIRouter(prefix="/api")


router.include_router(token.router)
router.include_router(pub.router)
router.include_router(router_ums.router)
router.include_router(router_dms.router)
router.include_router(router_grid.router)
