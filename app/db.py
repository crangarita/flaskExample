from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


db = SQLAlchemy()


class BaseModelMixin:

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def simple_filter(cls, **kwargs):
        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def simple_filter_paginate(cls, page, per_page, **kwargs):
        return cls.query.filter_by(**kwargs).paginate(page=page, per_page=per_page)

    @classmethod
    def simple_search_paginate(cls, page, per_page, param):
        return cls.query.filter(param).paginate(page=page, per_page=per_page)

    @classmethod
    def simple_filter_unique(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def native_query(cls, sql, **kwargs):
        engine = db.get_engine()
        conn = engine.connect()
        return conn.execute(text(sql))
