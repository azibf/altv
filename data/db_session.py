import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    
    #engine = create_engine("postgresql+psycopg2://aialdmcjyfnyii:e75d4d771f35958f10fc2b99fe8b1b9d3bf283175e3ea6d3c162328090b50b00@ec2-3-228-75-39.compute-1.amazonaws.com:5432/dasjrcvnriics5")
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()