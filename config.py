
# 业务库开发环境配置
dev_biz_db = {
    # 数据库连接URL
    'url': 'mysql+pymysql://root:honghong@127.0.0.1:3306/costdb',
    'engine_args': {
        # 连接池大小
        'pool_size': 2,
        # 超过连接池大小最多创建的连接
        'max_overflow': 0,
        # 池中没有线程最多等待的时间，否则报错
        'pool_timeout': 30,
        # 多久之后对线程池中的线程进行一次连接回收
        'pool_recycle': -1,
    }
}

dev_biz_pgsql_db = {
    # 数据库连接URL
    'url': 'postgresql+psycopg2://cost:123456@127.0.0.1:5432/costdb',
    'engine_args': {
        # 连接池大小
        'pool_size': 2,
        # 超过连接池大小最多创建的连接
        'max_overflow': 0,
        # 池中没有线程最多等待的时间，否则报错
        'pool_timeout': 30,
        # 多久之后对线程池中的线程进行一次连接回收
        'pool_recycle': -1,
    }
}

# 业务库配置
biz_db = dev_biz_pgsql_db

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "c6d3998918fe3099adced3fb5a37895e957352cb579b999acf6e5108c3470d3e"
# 令牌算法
ALGORITHM = "HS256"
# 令牌有效时长，默认24*60分钟
ACCESS_TOKEN_EXPIRE_MINUTES = 60*8
# 令牌访问URL
TOKEN_URL = '/api/login'
