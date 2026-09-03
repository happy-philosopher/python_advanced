# Настройка асинхронного подключения к SQLite (app/database.py)


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///offline_library.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(engine,
                                 class_=AsyncSession,
                                 autocommit=False,
                                 autoflush=False,
                                 expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
