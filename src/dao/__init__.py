from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engin = create_engine('sqlite:///database\\data.db', echo=True)
smkr = sessionmaker(bind=engin)
