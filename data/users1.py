import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from . import db_session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    ed_level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    vk = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_hours = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    news = orm.relation("News", back_populates='user')
    actions = orm.relation("Actions", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Actions(SqlAlchemyBase, UserMixin):
    __tablename__ = 'actions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')


class News(SqlAlchemyBase, UserMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')


class Books(SqlAlchemyBase, UserMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_checked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


class Maps(SqlAlchemyBase, UserMixin):
    __tablename__ = 'maps'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_counter = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
