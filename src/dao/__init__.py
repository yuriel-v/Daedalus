from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

engin = create_engine(getenv("DATABASE_URL").split(', ')[0], echo=(getenv("DAEDALUS_ENV").upper() == "DSV"))
smkr = sessionmaker(bind=engin)
if getenv("DAEDALUS_ENV").upper() == "DSV":
    dsvengin = create_engine(getenv("DATABASE_URL").split(', ')[1], echo=True)
    dsvsmkr = sessionmaker(bind=dsvengin)
else:
    dsvengin = None
    dsvsmkr = None
