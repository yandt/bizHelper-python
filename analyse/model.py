import random
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Status(Enum):
    SUCCESS = 'SUCCESS'
    EXECUTING = 'EXECUTING'
    FAILED = 'FAILED'
    STARTED = 'STARTED'
    FINISHED = 'FINISHED'
    FETCHING = 'FETCHING'


class ExecuteLog(BaseModel):
    key: str = str(uuid.uuid4())
    time: datetime = datetime.now()
    status: Status
    command: Optional[str]
    exec: Optional[float]
    fetch: Optional[float]
    rows: Optional[int]
    message: Optional[str]
    sql: Optional[str]

    class Config:
        orm_mode = True
