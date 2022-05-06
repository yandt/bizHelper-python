from fastapi import APIRouter
from biz.api.grid import api_connect, api_console

router = APIRouter(prefix="/grid")

router.include_router(api_connect.router)
router.include_router(api_console.router)
