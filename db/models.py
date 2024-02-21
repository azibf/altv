from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)



class Pool(Base):
    __tablename__ = "pools"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    golden_image_id = Column(Integer)
    naming_pattern = Column(String)
    number = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))