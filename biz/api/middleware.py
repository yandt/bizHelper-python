import time

from fastapi import FastAPI, Request, status
from starlette.middleware.gzip import GZipMiddleware
import re

from biz.api.exceptions import ApiException
from biz.api.oauth2 import getUserOnRequest
from config import TOKEN_URL


def checkPathOnRuleList(path: str, method: str, rules: dict):
    """
    检查path:method在rules中是否有权限
    :param path:
    :param method:
    :param rules: 格式为{"路径":1有权限｜0无权限}
    :return:
    """
    cur = '%s:%s' % (path, method.lower())

    def keys_func(d):
        rule = d[0]
        if rule == cur:
            return True
        if cur.startswith(rule):
            return True
        patter = re.sub(r'\/', '\\/', rule)
        patter = re.sub(r'\{\w+\}', '\\\\w+', patter)
        if re.match(patter, cur) is None:
            return False
        return True

    rules = sorted(rules.items(), key=lambda d: d[0].count('/'), reverse=True)
    rules_filter = filter(keys_func, rules)
    rows = list(rules_filter)
    print(rows)
    if len(rows) == 0:
        return True
    for row in rows:
        if row[1] == 1:
            return True
        else:
            return False
    return True


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time * 1000)
        return response

    @app.middleware("http")
    async def check_user_rule(request: Request, call_next):
        """
        通用TOKEN传入的后台授权路径检查权限
        :param request:
        :param call_next:
        :return:
        """
        if request.url.path != TOKEN_URL:
            user = await getUserOnRequest(request)
            if hasattr(user, 'back'):
                back_paths = user.back
                has = checkPathOnRuleList(request.url.path, request.method, back_paths)
                if not has:
                    raise ApiException('您无权访问此功能', status.HTTP_403_FORBIDDEN)

        response = await call_next(request)
        return response
