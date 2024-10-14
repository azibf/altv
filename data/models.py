import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from . import db_session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ip = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pools = orm.relationship("Pool", back_populates="user")


class Pool(SqlAlchemyBase, UserMixin):
    __tablename__ = "pools"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    golden_image = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    naming = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    node = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    vmids = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")
