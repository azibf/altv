from sqlalchemy import orm, Column, String, Integer, ForeignKey, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String)
    password = Column(String)
    node = orm.relation("PhysicalNode", back_populates='owner')    
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    
class PhysicalNode(SqlAlchemyBase):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String)
    user = Column(String)
    password = Column(String)
    verify_ssl = Column(Boolean, default=False)
    service = Column(String, default="PVE")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = orm.relation("User")


class DesktopPool(SqlAlchemyBase):
    __tablename__ = 'pool'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    node = Column(String)
    golden_image_id = Column(Integer, ForeignKey("vm.id"))
    golden_image = orm.relation("VirtualMachines")
    vm = orm.relation("VirtualMachine", back_populates='pool')


class VirtualMachines(SqlAlchemyBase):
    __tablename__ = 'vm'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey("pool.id"))
    pool = orm.relation('DesktopPool')
    vm = orm.relation("DesktopPool", back_populates='golden_image')