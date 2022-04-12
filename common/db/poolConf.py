from abc import ABC, abstractmethod


class BaseConf(ABC):
    def __init__(self,
                 pool_size: int = 5,
                 max_overflow: int = 0,
                 pool_timeout: int = 30,
                 pool_recycle: int = -1,
                 *args, **kwargs
                 ):
        """
        连接池配置基类
        :param pool_size: 连接池大小
        :param max_overflow: 超过连接池大小最多创建的连接
        :param pool_timeout: 池中没有线程最多等待的时间，否则报错
        :param pool_recycle: 多久之后对线程池中的线程进行一次连接回收
        """
        self.pool_size: int = pool_size
        self.max_overflow: int = max_overflow
        self.pool_timeout: int = pool_timeout
        self.pool_recycle: int = pool_recycle
        # 深copy一份默认设置属性集
        self.__args: dict = self.__dict__.copy()

    @abstractmethod
    def get_url(self):
        ...

    def get_engine_args(self):
        args = {}
        for key in self.__args.keys():
            args[key] = self.__dict__.get(key)
        return args


class MysqlConf(BaseConf):
    def __init__(self,
                 uid: str,
                 pwd: str,
                 database: str,
                 host: str,
                 port: int,
                 *args, **kwargs):
        """
        Mysql数据库配置类
        :param uid: 连接用户名
        :param pwd: 连接密码
        :param database: 数据库名
        :param host: 数据库地址
        :param port: 数据库端口
        """
        super(MysqlConf, self).__init__(*args, **kwargs)
        self.uid: str = uid
        self.pwd: str = pwd
        self.database: str = database
        self.host: str = host
        self.port: int = port

    def get_url(self):
        return "mysql+pymysql://{uid}:{pwd}@{host}:{port}/{database}".format(**self.__dict__)
