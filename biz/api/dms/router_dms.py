from fastapi import APIRouter
from biz.api.dms import api_dict

router = APIRouter(prefix="/dms")

router.include_router(api_dict.router)
