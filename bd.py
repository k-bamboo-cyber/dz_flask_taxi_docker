"""Working with databases over ORM sqlalchemy."""
from contextlib import contextmanager
from typing import Any

import dateutil
from sqlalchemy import Column, Integer, String, create_engine, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

# engine - пул соединений к БД
engine = create_engine('postgresql://postgres:postgres@localhost:5432/mydatabase')

# declarative_base - фабричная функция, возвращающая базовый класс, от которого произойдет наследование класса с
# моделью.
Base = declarative_base()
# создание новой сессии, для выполнения действий
Session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))


@contextmanager
def session_scope() -> Any:
    """Создание сессии."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Drivers(Base):
    """Класс для описания таблицы Drivers."""

    __tablename__ = 'drivers'  # имя таблицы

    # Атрибуты класса описывают колонки таблицы, их типы данных и ограничения
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Идентификатор водителя")
    name = Column(String(100), nullable=False, comment="Имя водителя")
    car = Column(String(100), nullable=False, comment="Описание машины водителя")

    def select_driver(self, id: int) -> Any:
        """Поиск водителя."""
        with session_scope() as session:
            res = session.query(Drivers).filter(Drivers.id == id).all()
            print(res)
            return res

    def insert_driver(self, name: str, car: str) -> Any:
        """Добавление водителя в систему."""
        with session_scope() as session:
            session.add(Drivers(name=name, car=car))
            session.commit()

    def delete_driver(self, id: int) -> Any:
        """Удаление водителя."""
        with session_scope() as session:
            session.query(Drivers).filter(Drivers.id == id).delete()
            session.commit()

    def repr(self) -> str:
        """Переопределение печати водителей."""
        return str("<Driver (id={0}, name={1}, car={2}>".format(
            self.id,
            self.name,
            self.car))


class Clients(Base):
    """Класс для описания таблицы Drivers."""

    __tablename__ = "clients"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    is_vip = Column(Boolean, nullable=False)

    def select_client(self, id: int) -> Any:
        """Поиск клиента."""
        with session_scope() as session:
            res = session.query(Clients).filter(Clients.id == id).all()
            print(res)
            return res

    def insert_client(self, name: str, is_vip: bool) -> Any:
        """Добавление клиента."""
        with session_scope() as session:
            session.add(Clients(name=name, is_vip=is_vip))
            session.commit()

    def delete_client(self, id: int) -> Any:
        """Удаление клиента."""
        with session_scope() as session:
            session.query(Clients).filter(Clients.id == id).delete()
            session.commit()

    def repr(self) -> str:
        """переопределение печати клиентов."""
        return str("<Client (id={0}, name={1}, is_vip={2}>"
                   .format(self.id,
                           self.name,
                           self.is_vip))


class Orders(Base):
    """Класс для описания таблицы Orders."""

    __tablename__ = 'orders'
    id = Column(Integer, autoincrement=True, primary_key=True)
    address_from = Column(String, nullable=False)
    address_to = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    date_created = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    def select_order(self, id: int) -> Any:
        """Выбор заказа."""
        with session_scope() as session:
            res = session.query(Orders).filter(Orders.id == id).all()
            return res

    def insert_order(self, address_from: str, address_to: str, client_id: int, driver_id: int, date_cr: str,
                     status: str) \
            -> Any:
        """Добавление заказа."""
        with session_scope() as session:
            session.add(Orders(address_from=address_from, address_to=address_to, client_id=client_id,
                               driver_id=driver_id, date_created=dateutil.parser.parse(date_cr), status=status))
            session.commit()

    def update_order_in_progress(self, id: int, new_status: str) -> Any:
        """обновление статуса заказа на in_progress ."""
        with session_scope() as session:
            session.query(Orders).filter(Orders.id == id).update({Orders.status: new_status}
                                                                 )
            session.commit()

    def update_order_not_accepted(self, id: int, new_status: str, new_date_cr: str, new_driver: int,
                                  new_client: int) -> Any:
        """изменение заказа для заказа со статусом not accepted ."""
        with session_scope() as session:
            session.query(Orders).filter(Orders.id == id).update({Orders.status: new_status,
                                                                  Orders.date_created: dateutil.parser.parse(
                                                                      new_date_cr),
                                                                  Orders.driver_id: new_driver,
                                                                  Orders.client_id: new_client})
            session.commit()

    def __repr__(self) -> str:
        """переопределение печати заказов."""
        return str({"id": self.id, "address_from": self.address_from, "address_to": self.address_to,
                    "client_id": self.client_id, "driver_id": self.driver_id, "date_created": self.date_created,
                    "status": self.status})


# создание таблиц если они не существуют
Base.metadata.create_all(engine)
