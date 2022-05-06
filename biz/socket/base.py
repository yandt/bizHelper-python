from fastapi import HTTPException

from biz.api.oauth2 import getCurrentUser


class SocketClient:
    def __init__(self, sio, namespace):
        self.__current_user = None
        self.__sio = sio
        self.__namespace = namespace

    async def emit(self, event, data=None, to=None, room=None, skip_sid=None, callback=None, ignore=False, **kwargs):
        if not ignore:
            await self.__sio.emit(event, data, to, room, skip_sid, self.__namespace, callback, **kwargs)

    async def getUserInfo(self, token: str):
        current_user = await getCurrentUser(token)
        self.__current_user = current_user
        return current_user
