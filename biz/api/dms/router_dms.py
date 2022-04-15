from fastapi import APIRouter
from biz.api.dms import api_dict, api_menu

router = APIRouter(prefix="/dms")

router.include_router(api_dict.router)
router.include_router(api_menu.router)

