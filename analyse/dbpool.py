import asyncio

import jaydebeapi
from analyse.conf import jdbc, jars
from biz.api.exceptions import ApiException


class Dbpool:
    def __init__(self, jdbc_name, conn_str, username, password, namespace=None):
        if jdbc.get(jdbc_name) is None:
            raise ApiException('不支持数据库类型：%s' % jdbc_name)
        jdbc_config = jdbc[jdbc_name]
        self.__jdbc_class = jdbc_config['clazz']
        self.__conn_str = conn_str
        self.__username = username
        self.__password = password
        self.__namespace = namespace
        self.__conn()

    def __conn(self):
        self.__connect = jaydebeapi.connect(
            self.__jdbc_class,
            self.__conn_str,
            [self.__username, self.__password],
            jars
        )
        # self.__conn = pyodbc.connect(self.__conn_str)
        # self.__conn.setdecoding(pyodbc.SQL_CHAR, encoding='gbk')
        # self.__conn.setdecoding(pyodbc.SQL_WCHAR, encoding='gbk')
        # self.__conn.setencoding(encoding='gbk')
        self.__cursor = self.__connect.cursor()

    @staticmethod
    def __convert_params(sql, params):
        # return sql.format(**params), []
        return sql, params

    async def fetch_all(self, sql, params={}):
        cp = self.__convert_params(sql, params)
        try:
            return await self.fetch_cursor(cp[0], cp[1] if cp[1] is not None and len(cp[1]) > 0 else None).fetchall()
        except Exception as r:
            raise r

    async def fetch_one(self, sql, params={}):
        cp = self.__converta_params(sql, params)
        return await self.fetch_cursor(cp[0], cp[1] if cp[1] is not None and len(cp[1]) > 0 else None).fetchone()

    async def fetch_cursor(self, sql, params={}) -> jaydebeapi.Cursor:
        cp = self.__convert_params(sql, params)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__cursor.execute, cp[0],
                                   cp[1] if cp[1] is not None and len(cp[1]) > 0 else None)
        return self.__cursor

    async def execute(self, sql, params={}):
        cp = self.__converta_params(sql, params)
        await self.fetch_cursor(cp[0], cp[1] if cp[1] is not None and len(cp[1]) > 0 else None)
        return self.__cursor.rowcount

    @staticmethod
    def fetch_columns(cursor):
        return [desc[0] for desc in cursor.description]

    def close(self):
        self.__cursor.close()
        self.__connect.close()


