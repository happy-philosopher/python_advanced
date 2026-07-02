# Реализуйте эндпойнт /search с параметрами query (строка поиска) и
# limit (количество результатов, по умолчанию 10).


from fastapi import FastAPI, Query
from typing import List, Dict, Any


app = FastAPI()
MOCK_DATA = [
    {
        "id": 1,
        "title": "Основы Python",
        "description": "Курс для начинающих: синтаксис, типы данных, базовые конструкции."
    },
    {
        "id": 2,
        "title": "Продвинутый Python",
        "description": "Глубокое погружение: генераторы, контекстные менеджеры, метаклассы."
    },
    {
        "id": 3,
        "title": "Разработка API на FastAPI",
        "description": "Создание RESTful и асинхронных API, валидация данных, работа с зависимостями."
    },
    {
        "id": 4,
        "title": "Паттерны проектирования в Python",
        "description": "Стратегия, наблюдатель, декоратор, одиночка и другие паттерны с примерами."
    },
    {
        "id": 5,
        "title": "Асинхронное программирование с asyncio",
        "description": "Корутины, event loop, конкурентное выполнение задач, aiohttp."
    },
    {
        "id": 6,
        "title": "Работа с базами данных в Python",
        "description": "SQLAlchemy, PostgreSQL, миграции, транзакции и оптимизация запросов."
    },
    {
        "id": 7,
        "title": "Тестирование Python-приложений",
        "description": "Pytest, фикстуры, моки, покрытие кода, интеграционные тесты."
    },
    {
        "id": 8,
        "title": "Docker и контейнеризация для Python-разработчиков",
        "description": "Сборка образов, docker-compose, запуск приложений в контейнерах."
    },
    {
        "id": 9,
        "title": "Telegram-боты на Python",
        "description": "Создание ботов с aiogram, обработка команд, работа с состояниями."
    },
    {
        "id": 10,
        "title": "Принципы SOLID и чистая архитектура",
        "description": "Разбор пяти принципов SOLID, разделение ответственности, проектирование масштабируемых систем."
    }
]


@app.get("/search")
def search(
    query: str = Query(min_length=1, description="Строка поиска"),
    limit: int = Query(10, ge=1, le=100, description="Количество результатов (1–100)")) -> List[Dict[str, Any]]:
    """
    Поиск по title и description.
    Возвращает список найденных элементов (не более limit).
    """
    query_lower = query.lower()
    results = [
        item for item in MOCK_DATA
        if query_lower in item["title"].lower() or query_lower in item["description"].lower()
    ]
    return results[:limit]
