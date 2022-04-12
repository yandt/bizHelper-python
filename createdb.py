from importlib import import_module

from sqlalchemy import Table

from biz import conn
from biz.model.ums import User
from biz.service.ums import userService

schema = input('请输入架构名：')
if schema == '':
    print('架构名不得为空')
    exit()
try:
    module = import_module('biz.model.%s' % schema)
except Exception as e:
    print('架构%s无效' % schema)
    print(e)
    exit()

dbname = input('请输入创建表的className，用","分隔表名（如输入all则创建架构内所有表）:')
if dbname == '':
    print('请输入表名')
    exit()

is_cover = input('是否删除原表,输入（YYY）表示删除:')

if is_cover == 'YYY':
    cover = '覆盖'
else:
    cover = ''

tables_name = '所有表'
if dbname != 'all':
    tables_name = dbname
else:
    dbname = ''

print('开始%s创建架构%s下的%s...' % (cover, schema, tables_name))
engine = conn.get_engine()
engine.echo = True

tables = dbname.split(',')
tables = [getattr(module, t).__table__ for t in tables]

if is_cover == 'YYY':
    print('开始删除表%s' % tables)
    if len(dbname) == 0:
        module.drop_db(engine)
    else:
        module.drop_db(engine, tables)

print('开始创建表%s' % tables)
if len(dbname) == 0:
    module.init_db(engine)
else:
    module.init_db(engine, tables)

print('表格建立成功')

if schema == 'ums':
    # 开始创建管理员角色
    u: User = userService.getUser(nick='admin')
    if u is None:
        u = User(nick='admin', name='系统管理员', validity='valid')
        userService.save(u, 'admin')
