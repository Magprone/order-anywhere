import sqlalchemy
from data.db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class ProfileType(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'profile_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    profile_type = sqlalchemy.Column(sqlalchemy.String)
    account_id = sqlalchemy.Column(sqlalchemy.Integer)
