import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path


# Добавляем корневую папку проекта в PYTHONPATH
# ROOT_DIR = Path(__file__).resolve().parents[1]  # Поднимаемся на 2 уровня вверх
# sys.path.insert(0, str(ROOT_DIR))  # Теперь Python видит папку src


from ..src.main import app
from ..src.app.database import get_db, AsyncSessionLocal
from ..src.app.models import Base


TEST_DB_URL = "sqlite+aiosqlite:///test_offline_library.db"


@pytest.fixture(scope="session")
def engine():
    return create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )


@pytest.fixture(scope="session")
def init_db(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
