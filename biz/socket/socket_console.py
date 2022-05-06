from bidict import bidict
from fastapi import HTTPException

from analyse import utils
from biz.api.exceptions import ApiException
from biz.api.middleware import checkPathOnRuleList
from biz.model.grid import Console
from biz.service.grid import consoleService, connectService
from biz.socket.base import SocketClient

user_sid = bidict()

NAMESPACE: str = '/console'


def register_event(socket_io):
    scli = SocketClient(socket_io, NAMESPACE)

    # 事件函数
    async def connect(sid, environ, auth):
        try:
            current_user = await scli.getUserInfo(auth['token'])
        except HTTPException as e:
            await scli.emit('error', f'连接失败，原因：{e.detail}', sid)
            return
        has = checkPathOnRuleList('/api/grid/console/execute', 'put', current_user.back)
        if not has:
            await scli.emit('error', f'您没有控制台执行查询权限', sid)
            return

        # user_sid[sid] = current_user.uid
        await scli.emit('connect_success', f'连线成功！', sid)

    async def query(sid, params):
        if 'consoleId' in params:
            c: Console = consoleService.getOne(params['consoleId'])
            if c is None:
                raise ApiException('控制台信息不存在')
            _connect = connectService.getDatabaseConnect(c.connectId)
            await utils.execute_sql(_connect, params['content'], scli, sid, push_logs=True)
            _connect.close()
            await scli.emit('finish', f'查询成功', sid)

    async def disconnect(sid):
        if sid in user_sid:
            user_sid.pop(sid)

    socket_io.on('disconnect', disconnect, namespace=NAMESPACE)
    socket_io.on('query', query, namespace=NAMESPACE)
    socket_io.on('connect', connect, namespace=NAMESPACE)
