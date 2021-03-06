import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Menu(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'menus'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    restaurant = orm.relation('Restaurant', back_populates='menu')

    categories = orm.relation('Category', back_populates='menu', lazy='subquery', cascade="all,delete", passive_deletes=True)
    items = orm.relation('MenuItem', back_populates='menu', lazy='subquery', cascade="all,delete", passive_deletes=True)
