# ORM-модели со связями (app/models.py)


from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    bio: Mapped[str] = Column(String(500), nullable=True)

    books = relationship(
        'Book',
        back_populates='author',
        cascade='all, delete-orphan'  # Каскадное удаление книг при удалении автора
    )


class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(200), nullable=False)
    author_id: Mapped[int] = Column(ForeignKey('authors.id'), nullable=False)
    year: Mapped[int] = Column(Integer, nullable=False)
    pages: Mapped[int] = Column(Integer, nullable=False)

    author = relationship('Author', back_populates='books')
    orders = relationship('Order', back_populates='book')


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = Column(String(150), nullable=False)
    phone: Mapped[str] = Column(String(15), nullable=False)
    email: Mapped[str] = Column(String(150), unique=True, nullable=False)

    orders = relationship(
        'Order',
        back_populates='client',
        cascade='all, delete-orphan'  # Каскадное удаление заказов при удалении клиента
    )


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = Column(ForeignKey('clients.id'), nullable=False)
    book_id: Mapped[int] = Column(ForeignKey('books.id'), nullable=False)
    issue_date: Mapped[date] = Column(Date, nullable=False)
    return_date: Mapped[date] = Column(Date, nullable=True)

    client = relationship('Client', back_populates='orders')
    book = relationship('Book', back_populates='orders')
