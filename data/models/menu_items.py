import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class MenuItem(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'menu_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    item_image = sqlalchemy.Column(sqlalchemy.String, default='no_image.png')

    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)

    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'))
    category = orm.relation('Category')

    menu_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('menus.id'))
    menu = orm.relation('Menu')
