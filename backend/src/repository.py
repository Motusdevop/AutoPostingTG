from typing import List

from sqlalchemy import insert, text

from database import create_tables, drop_tables, session_factory
from models import Base, ChannelORM, UserORM


class CRUDRepository:
    model = Base

    @classmethod
    def add(cls, obj):
        with session_factory() as session:
            obj: cls.model
            session.add(obj)
            session.commit()

    @classmethod
    def get(cls, id: int) -> Base:
        with session_factory() as session:
            return session.query(cls.model).filter(cls.model.id == id).first()

    @classmethod
    def get_all(cls) -> List[Base]:
        with session_factory() as session:
            return session.query(cls.model).all()

    @classmethod
    def update(cls, obj: Base):
        with session_factory() as session:
            try:
                # Используем merge для автоматического обновления или вставки
                session.merge(obj)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    @classmethod
    def delete(cls, id: int):
        with session_factory() as session:
            session.query(cls.model).filter(cls.model.id == id).delete()
            session.commit()


class ChannelRepository(CRUDRepository):
    model = ChannelORM

    @classmethod
    def check_exist(cls, name: str):
        with session_factory() as session:
            obj = session.query(cls.model).filter(cls.model.name == name).first()

            if not obj is None:
                return True
            return False

    @classmethod
    def get_actives(cls) -> List[ChannelORM]:
        with session_factory() as session:
            return session.query(cls.model).filter(cls.model.active == True).all()


class UserRepository(CRUDRepository):
    model = UserORM


if __name__ == "__main__":
    create_tables()

    UserRepository.add(UserORM(username="test", password="test"))
    print(UserRepository.get(1).username)

    ChannelRepository.add(
        ChannelORM(
            name="Test",
            chat_id=-1002432783068,
            share_link="@testing_autopost",
            path_to_source_dir="path",
            path_to_done_dir="path",
        )
    )

    print(f"{ChannelRepository.get(1).name = }")
    print(ChannelRepository.get_all())

    drop_tables()
