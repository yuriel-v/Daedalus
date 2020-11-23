from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

engin = create_engine(getenv("DATABASE_URL"), echo=True)
smkr = sessionmaker(bind=engin)
