import socketio
from fastapi import FastAPI

import config
from biz.api.root import router_root
from biz.api.exceptions import register_exception_handler
from biz.api.middleware import register_middleware
from biz.socket import socket_console

app = FastAPI(title="业务助手",
              description="业务助手API",
              docs_url="/swagger/docs",
              openapi_url="/swagger/openapi",  # 此处如修改，请同时修前端 /ums/rule/service.ts 文件中的数据路径
              version='0.01'
              )
# 所有路由
app.include_router(router_root.router)

# 注册异常处理类
register_exception_handler(app)
# 注册中间件
register_middleware(app)


sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False)
    # client_manager=socketio.AsyncRedisManager(f'{config.REDIS_URL}/0'))
app.mount('/', socketio.ASGIApp(socketio_server=sio, socketio_path='ws'))  # 使用默认的socket path

socket_console.register_event(sio)
