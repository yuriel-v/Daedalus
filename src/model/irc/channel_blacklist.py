from model import Base
from sqlalchemy import Column, BigInteger, ForeignKey


class ChannelBlacklist(Base):
    __tablename__ = 'chblacklist'

    server_id = Column(BigInteger, ForeignKey('server.id'), primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
