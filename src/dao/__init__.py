from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

from dao.studentdao import StudentDao
from dao.subjectdao import SubjectDao
from dao.schedulerdao import SchedulerDao

engin = create_engine(getenv("DATABASE_URL").split(', ')[0], echo=getenv("DAEDALUS_ENV").upper() == "DSV")
smkr = sessionmaker(bind=engin)

stdao = StudentDao()
sbdao = SubjectDao()
scdao = SchedulerDao()
