from sqlalchemy import create_engine
from os import getenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

database_url = getenv("DATABASE_URL").split(', ')[0]
if not database_url.startswith('postgresql'):
    database_url = database_url.split(':')
    database_url[0] = 'postgresql'
    database_url = ':'.join(database_url)

engin = create_engine(
    database_url,
    echo=(getenv("DAEDALUS_ENV").upper() == "DEV"),
    connect_args={'connect_timeout': 3},
    pool_pre_ping=True
)

if getenv("DAEDALUS_ENV").upper() == "DEV":
    try:
        devengin = create_engine(getenv("DATABASE_URL").split(', ')[1], echo=True, pool_pre_ping=True)
    except IndexError:
        devengin = None
else:
    devengin = None

DBSession = scoped_session(sessionmaker(bind=engin))
Base = declarative_base()


def initialize_sql(engine):
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
