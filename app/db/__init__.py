import sqlalchemy as sa
from sqlalchemy import orm, MetaData

from .base import Base as Base_

meta = MetaData(naming_convention={
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
})

Base: Base_ = orm.declarative_base(cls=Base_, metadata=meta)

session = None
engine = None


def setup_db(url=None, force=False):
    global engine, session
    if not force and session is not None:
        return
    url = url or 'sqlite:///./app.db'
    engine = sa.create_engine(url, echo=False)
    Session = orm.sessionmaker(bind=engine, autoflush=False)
    session = Session()


setup_db()
