# Реализация FastAPI с CRUD-эндпоинтами (main.py)


from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import FastAPI, HTTPException, Depends

from app.crud import (
    create_author, get_author, get_authors, update_author, delete_author,
    create_book, get_book, get_books, update_book, delete_book,
    create_client, get_client, get_clients, update_client, delete_client,
    create_order, get_order, get_orders, update_order, delete_order
)
from app.schemas import (
    AuthorCreate, AuthorUpdate, AuthorDB,
    BookCreate, BookUpdate, BookDB,
    ClientCreate, ClientUpdate, ClientDB,
    OrderCreate, OrderUpdate, OrderDB
)
from app.database import get_db


app = FastAPI(title='Оффлайн-библиотека')


# Зависимость для сессии БД
async def db_session():
    async for session in get_db():
        yield session


# ---------- Авторы ----------

@app.post("/authors/", response_model=AuthorDB)
async def create_author_endpoint(author: AuthorCreate, db: AsyncSession = Depends(db_session)):
    return await create_author(db, author)


@app.get("/authors/", response_model=List[AuthorDB])
async def read_authors(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(db_session)):
    authors = await get_authors(db, skip, limit)
    return authors


@app.get("/authors/{author_id}", response_model=AuthorDB)
async def read_author(author_id: int, db: AsyncSession = Depends(db_session)):
    author = await get_author(db, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.put("/authors/{author_id}", response_model=AuthorDB)
async def update_author_endpoint(author_id: int, author_update: AuthorUpdate, db: AsyncSession = Depends(db_session)):
    author = await update_author(db, author_id, author_update)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.delete("/authors/{author_id}", response_model=bool)
async def delete_author_endpoint(author_id: int, db: AsyncSession = Depends(db_session)):
    success = await delete_author(db, author_id)
    if not success:
        raise HTTPException(status_code=404, detail="Author not found")
    return success


# ---------- Книги ----------

@app.post("/books/", response_model=BookDB)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(db_session)):
    return await create_book(db, book)


@app.get("/books/", response_model=List[BookDB])
async def read_books(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(db_session)):
    books = await get_books(db, skip, limit)
    return books


@app.get("/books/{book_id}", response_model=BookDB)
async def read_book(book_id: int, db: AsyncSession = Depends(db_session)):
    book = await get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookDB)
async def update_book_endpoint(book_id: int, book_update: BookUpdate, db: AsyncSession = Depends(db_session)):
    book = await update_book(db, book_id, book_update)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.delete("/books/{book_id}", response_model=bool)
async def delete_book_endpoint(book_id: int, db: AsyncSession = Depends(db_session)):
    success = await delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return success


# ---------- Клиенты ----------

@app.post("/clients/", response_model=ClientDB)
async def create_client_endpoint(client: ClientCreate, db: AsyncSession = Depends(db_session)):
    return await create_client(db, client)


@app.get("/clients/", response_model=List[ClientDB])
async def read_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(db_session)):
    clients = await get_clients(db, skip, limit)
    return clients


@app.get("/clients/{client_id}", response_model=ClientDB)
async def read_client(client_id: int, db: AsyncSession = Depends(db_session)):
    client = await get_client(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=ClientDB)
async def update_client_endpoint(client_id: int, client_update: ClientUpdate, db: AsyncSession = Depends(db_session)):
    client = await update_client(db, client_id, client_update)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.delete("/clients/{client_id}", response_model=bool)
async def delete_client_endpoint(client_id: int, db: AsyncSession = Depends(db_session)):
    success = await delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return success


# ---------- Заказы ----------

@app.post("/orders/", response_model=OrderDB)
async def create_order_endpoint(order: OrderCreate, db: AsyncSession = Depends(db_session)):
    return await create_order(db, order)


@app.get("/orders/", response_model=List[OrderDB])
async def read_orders(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(db_session)):
    orders = await get_orders(db, skip, limit)
    return orders


@app.get("/orders/{order_id}", response_model=OrderDB)
async def read_order(order_id: int, db: AsyncSession = Depends(db_session)):
    order = await get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/orders/{order_id}", response_model=OrderDB)
async def update_order_endpoint(order_id: int, order_update: OrderUpdate, db: AsyncSession = Depends(db_session)):
    order = await update_order(db, order_id, order_update)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.delete("/orders/{order_id}", response_model=bool)
async def delete_order_endpoint(order_id: int, db: AsyncSession = Depends(db_session)):
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return success
