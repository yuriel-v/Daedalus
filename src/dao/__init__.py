from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

engin = create_engine(
    getenv("DATABASE_URL").split(', ')[0],
    echo=(getenv("DAEDALUS_ENV").upper() == "DEV"),
    connect_args={'connect_timeout': 3},
    pool_pre_ping=True
)
smkr = sessionmaker(bind=engin)
if getenv("DAEDALUS_ENV").upper() == "DEV":
    devengin = create_engine(getenv("DATABASE_URL").split(', ')[1], echo=True, pool_pre_ping=True)
    devsmkr = sessionmaker(bind=devengin)
else:
    devengin = None
    devsmkr = None
