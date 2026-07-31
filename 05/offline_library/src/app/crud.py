# Функции CRUD


from .models import Author, Book, Client, Order
from .schemas import AuthorCreate, AuthorUpdate, BookCreate, BookUpdate, ClientCreate, ClientUpdate, OrderCreate, OrderUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional


# ------- Авторы -------

async def create_author(db: AsyncSession, author: AuthorCreate) -> Author:
    db_author = Author(**author.model_dump())
    db.add(db_author)
    await db.commit()
    await db.refresh(db_author)
    return db_author


async def get_author(db: AsyncSession, author_id: int) -> Optional[Author]:
    result = await db.execute(select(Author).where(Author.id == author_id))
    return result.scalar()


async def get_authors(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Author]:
    query = select(Author).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_author(db: AsyncSession, author_id: int, author_update: AuthorUpdate) -> Optional[Author]:
    author = await get_author(db, author_id)
    if not author:
        return None
    update_data = author_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(author, key, value)
    await db.commit()
    await db.refresh(author)
    return author


async def delete_author(db: AsyncSession, author_id: int) -> bool:
    author = await get_author(db, author_id)
    if not author:
        return False
    await db.delete(author)
    await db.commit()
    return True


# ------- Книги -------

async def create_book(db: AsyncSession, book: BookCreate) -> Book:
    db_book = Book(**book.model_dump())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book


async def get_book(db: AsyncSession, book_id: int) -> Optional[Book]:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar()


async def get_books(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Book]:
    query = select(Book).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_book(db: AsyncSession, book_id: int, book_update: BookUpdate) -> Optional[Book]:
    book = await get_book(db, book_id)
    if not book:
        return None
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: int) -> bool:
    book = await get_book(db, book_id)
    if not book:
        return False
    await db.delete(book)
    await db.commit()
    return True


# ------- Клиенты -------

async def create_client(db: AsyncSession, client: ClientCreate) -> Client:
    db_client = Client(**client.model_dump())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client


async def get_client(db: AsyncSession, client_id: int) -> Optional[Client]:
    result = await db.execute(select(Client).where(Client.id == client_id))
    return result.scalar()


async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Client]:
    query = select(Client).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_client(db: AsyncSession, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    client = await get_client(db, client_id)
    if not client:
        return None
    update_data = client_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    await db.commit()
    await db.refresh(client)
    return client


async def delete_client(db: AsyncSession, client_id: int) -> bool:
    client = await get_client(db, client_id)
    if not client:
        return False
    await db.delete(client)
    await db.commit()
    return True


# ------- Заказы -------

async def create_order(db: AsyncSession, order: OrderCreate) -> Order:
    db_order = Order(**order.model_dump())
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_order(db: AsyncSession, order_id: int) -> Optional[Order]:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar()


async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
    query = select(Order).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_order(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    order = await get_order(db, order_id)
    if not order:
        return None
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)
    await db.commit()
    await db.refresh(order)
    return order


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    order = await get_order(db, order_id)
    if not order:
        return False
    await db.delete(order)
    await db.commit()
    return True
