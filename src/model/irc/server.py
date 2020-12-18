# Modelo de servidores, com suas configurações específicas.
from model import Base
from sqlalchemy import Column, BigInteger, Integer
from sqlalchemy.orm import relationship


class Server(Base):
    __tablename__ = "server"

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    server_owner = Column(BigInteger, nullable=False)
    welcome_channel = Column(BigInteger)
    default_role = Column(BigInteger)
    lowest_mod_role = Column(BigInteger)

    banned_channels = relationship("ChannelBlacklist", cascade='all, delete-orphan')
