import asyncio
import time
import uuid
from datetime import datetime

from engineio import AsyncServer
from fastapi.encoders import jsonable_encoder
from jaydebeapi import DatabaseError
from jpype import java

from analyse.dbpool import Dbpool
from analyse.model import ExecuteLog, Status
from analyse.sqlExtractors import SqlExtractors, SqlExtractor
from biz.api.exceptions import ApiException
from biz.socket.base import SocketClient


async def execute_sql(dbpool: Dbpool, sql: str, sio: SocketClient, to,
                      params: dict = None, push_logs: bool = True):
    sum_exec = 0
    sum_fetch = 0
    sum_rows = 0
    sum_success = 0
    sum_error = 0
    sql_extractors = SqlExtractors(sql)
    logs = [ExecuteLog(status=Status.STARTED, time=datetime.now(), key=str(uuid.uuid4()))]
    await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)
    await sio.emit('length', len(sql_extractors.extractors))

    for i in range(len(sql_extractors.extractors)):
        sql: SqlExtractor = sql_extractors.extractors[i]
        log = ExecuteLog(
            time=datetime.now(),
            key=str(uuid.uuid4()),
            status=Status.EXECUTING,
            command=sql.get_type(),
            sql=sql.raw,
            message='正在执行查询，请稍候...'
        )
        logs.append(log)
        await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)
        start_time = time.time()
        try:
            cursor = await dbpool.fetch_cursor(sql.sql, params)
            process_time = time.time() - start_time
            log.exec = round(process_time, 4)
            sum_exec += process_time
            await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)
            if cursor.rowcount >= 0:
                log.rows = cursor.rowcount
                log.status = Status.SUCCESS
                log.message = 'OK'
                sum_rows += log.rows
            else:
                log.status = Status.FETCHING
                log.message = '正在获取数据，请稍候...'
                await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)
                start_time = time.time()
                await sio.emit('new', {
                    'key': str(uuid.uuid4()),
                    'name': list(sql.tables)[0]
                }, to)
                columns = [desc[0] for desc in cursor.description]
                await sio.emit('header', columns, to)

                count = 0
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                    await sio.emit('row', jsonable_encoder(row, sqlalchemy_safe=False), to)
                    count += 1

                process_time = time.time() - start_time
                log.fetch = round(process_time, 4)
                log.rows = (count - 1) if count > 0 else 0
                log.status = Status.SUCCESS
                log.message = 'OK'
                sum_fetch += log.fetch
                sum_rows += log.rows
        except ApiException as e:
            log.message = e.message
            log.status = Status.FAILED
        except Exception as e:
            log.message = e.__str__()
            log.status = Status.FAILED
        finally:
            # print(jsonable_encoder(logs))
            if log.status == Status.SUCCESS:
                sum_success += 1
            elif log.status == Status.FAILED:
                sum_error += 1
            await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)

        await sio.emit('count', i + 1, to)

    logs.append(ExecuteLog(
        key=str(uuid.uuid4()),
        time=datetime.now(),
        status=Status.FINISHED,
        exec=round(sum_exec, 4),
        fetch=round(sum_fetch, 4),
        rows=sum_rows,
        message=f'成功：{sum_success}，失败：{sum_error}'
    ))
    await sio.emit('logs', jsonable_encoder(logs), to, ignore=not push_logs)
