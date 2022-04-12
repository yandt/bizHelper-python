from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from biz.conn import get_conn
from biz.model import ums, dms

models = []
engine = get_conn().get_engine()
engine.echo = True


def print_red_text(text):
    print("\033[0;31m\t%s\033[0m" % text)


def register_model():
    models.append(ums)
    models.append(dms)


def create_all_table(tables=None, checkfirst=True):
    for model in models:
        model.BASE.metadata.create_all(engine, tables, checkfirst)
        if tables is None:
            print_red_text("模块 %s 下所有数据表创建成功！" % model.__name__)
        else:
            print_red_text("模块 %s 下 [ %s ] 数据表创建成功！" % (model.__name__, tables))


def drop_all_table(tables=None, checkfirst=True):
    for model in models:
        model.BASE.metadata.create_all(engine, tables, checkfirst)
        if tables is None:
            print_red_text("模块 %s 下所有数据表删除成功！" % model.__name__)
        else:
            print_red_text("模块 %s 下 [ %s ] 数据表删除成功！" % (model.__name__, tables))


register_model()
# drop_all_table()
# create_all_table()
