# Тестирования FastAPI-приложения "Оффлайн-библиотека"

## Структура проекта

```
offline_library/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── schemas.py
│   ├── main.py
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_authors.py
│   ├── test_books.py
│   ├── test_clients.py
│   ├── test_orders.py
│   └── test_validation.py
├── alembic/
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```