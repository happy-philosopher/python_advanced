import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

import sys
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.main import app
from src.app.database import get_db
from src.app.models import Base, Author, Book, Client, Order  # Добавлены импорты моделей
from src.app.schemas import AuthorCreate, BookCreate, ClientCreate, OrderCreate
from src.app.crud import create_author, create_book, create_client, create_order

# Тестовая база данных в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем асинхронный движок для тестов
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)

# Создаем фабрику сессий
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для тестовой сессии БД"""
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    # Очистка после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session: AsyncSession) -> Generator:
    """Фикстура для тестового клиента FastAPI"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_author(db_session: AsyncSession) -> Author:
    """Фикстура для создания тестового автора"""
    author_data = AuthorCreate(
        name="Тестовый Автор",
        bio="Тестовая биография"
    )
    return await create_author(db_session, author_data)


@pytest.fixture(scope="function")
async def test_book(db_session: AsyncSession, test_author: Author) -> Book:
    """Фикстура для создания тестовой книги"""
    book_data = BookCreate(
        title="Тестовая Книга",
        author_id=test_author.id,
        year=2024,
        pages=300
    )
    return await create_book(db_session, book_data)


@pytest.fixture(scope="function")
async def test_client(db_session: AsyncSession) -> Client:
    """Фикстура для создания тестового клиента"""
    client_data = ClientCreate(
        full_name="Тестовый Клиент",
        phone="+79991234567",
        email="test@example.com"
    )
    return await create_client(db_session, client_data)


@pytest.fixture(scope="function")
async def test_order(db_session: AsyncSession, test_client: Client, test_book: Book) -> Order:
    """Фикстура для создания тестового заказа"""
    from datetime import date

    order_data = OrderCreate(
        client_id=test_client.id,
        book_id=test_book.id,
        issue_date=date(2024, 1, 1),
        return_date=date(2024, 1, 15)
    )
    return await create_order(db_session, order_data)