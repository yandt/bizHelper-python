from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import Session


class Pool:
    def __init__(self, config: dict):
        """
        初始化连接池
        :param config:
        """
        self.__url = config['url']
        self.__engine_args = config['engine_args']
        self.__engine = None

    def __create_engine(self):
        engine = create_engine(self.__url, **self.__engine_args)
        return engine

    def __create_session_factory(self):
        db_session = sessionmaker(bind=self.__create_engine().engine, expire_on_commit=False)
        return scoped_session(db_session)

    def get_engine(self):
        return self.__create_engine().engine

    def get_session(self) -> Session:
        db_session_factory = self.__create_session_factory()
        return db_session_factory()


