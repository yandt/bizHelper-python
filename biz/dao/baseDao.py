from biz.conn import get_session_scope
from sqlalchemy.orm import Query

from biz.model.base import PageList


def get_query(*entities) -> Query:
    with get_session_scope() as session:
        q = session.query(*entities).filter()
    return q


def get_page_list(entities: [], where: [], order_by: [], limit: int, offset: int):
    with get_session_scope() as session:
        total = session.query(*entities).filter(*where).count()
        q = session.query(*entities).filter(*where).order_by(*order_by).limit(limit).offset(offset)
        rows = q.all()
    return PageList(total=total, rows=rows)


def get_list(entities: [], where: [], order_by: []):
    with get_session_scope() as session:
        q = session.query(*entities).filter(*where).order_by(*order_by)
        rows = q.all()
    return rows
