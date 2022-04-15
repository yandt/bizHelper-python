from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import Session

import config


class Pool(object):
    __instance = None
    __engine = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def gen_engine(self):
        if not Pool.__engine:
            __url = config.biz_db['url']
            __engine_args = config.biz_db['engine_args']
            engine = create_engine(__url, **__engine_args)
            Pool.__engine = engine
        return Pool.__engine

    # def __create_session_factory(self):
    #     db_session = sessionmaker(bind=Pool.__engine, expire_on_commit=False)
    #     return scoped_session(db_session)
    #
    # def get_session(self) -> Session:
    #     db_session_factory = Pool.__create_session_factory()
    #     return db_session_factory()

    @property
    def session(self):
        self.gen_engine()
        session = scoped_session(sessionmaker(bind=Pool.__engine, expire_on_commit=False))
        return session()
