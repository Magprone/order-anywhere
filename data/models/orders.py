import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    price = sqlalchemy.Column(sqlalchemy.Integer)
    state = sqlalchemy.Column(sqlalchemy.String, default='Is not sent')  # Is not sent/Awaiting payment/In progress/Ready/Finished

    restaurant_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurants.id'))
    restaurant = orm.relation('Restaurant')

    restaurant_place_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('restaurant_places.id'))
    restaurant_place = orm.relation('RestaurantPlace')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')

    order_items = orm.relation('OrderItem', back_populates='order', lazy='subquery', cascade="all,delete", passive_deletes=True)
