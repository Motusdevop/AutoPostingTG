from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


class ChannelORM(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    chat_id = Column(Integer, nullable=False, unique=True)

    interval = Column(Integer, default=60 * 4)
    parse_mode = Column(String, default="html")

    active = Column(Boolean, default=False, nullable=False)

    path_to_source_dir = Column(String, nullable=False, unique=True)
    path_to_done_dir = Column(String, nullable=False, unique=True)
    path_to_except_dir = Column(String, nullable=True, unique=True)
