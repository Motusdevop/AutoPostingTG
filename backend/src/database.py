from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from loguru import logger

from settings import Settings, get_settings

from models import *

cfg = get_settings()

engine = create_engine(f"sqlite:///{cfg.database_name}.db", echo=cfg.debug)

session_factory = sessionmaker(engine)

def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created")

def drop_tables():
    Base.metadata.create_all(bind=engine)
    logger.warning("Tables dropped")

if __name__ == "__main__":
    create_tables()