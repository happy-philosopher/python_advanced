# Учебный проект "Оффлайн-библиотека"

## Структура проекта
```
offline_library/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── crud.py
│   └── schemas.py
├── alembic/
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── 9f0f8e20110c_initial_tables.py
│       └── ...
├── main.py
├── alembic.ini
├── offline_library.db
├── README.md
└── requirements.txt
```

## Запуск проекта
Alembic по умолчанию работает синхронно.
Асинхронные сессии оставляем для приложения (FastAPI), а для миграций используем синхронный движок.
Нужную строку закомментировать в файле ```alembic.ini```.

### Работа с Alembic (создание БД и миграции):
```
...
sqlalchemy.url = sqlite:///offline_library.db
# sqlalchemy.url = sqlite+aiosqlite:///offline_library.db
...
```

### Нормальная работа программы:
```
...
# sqlalchemy.url = sqlite:///offline_library.db
sqlalchemy.url = sqlite+aiosqlite:///offline_library.db
...
```
1. Инициализация таблиц для базы данных
```alembic revision --autogenerate -m "Initial tables"```

2. Сгенерировать БД:
```alembic upgrade head```

3. Запустить приложение:
```uvicorn main:app --reload```

### Можно проверить работу программы (эндпоинты) через Postman или curl, или через SwaggerUI:
http://127.0.0.1:8000/docs

## Краткий итог:
- Модели ORM описывают структуру данных со связями 1:N.
- Alembic управляет миграциями.
- FastAPI реализует CRUD для всех сущностей с валидацией через Pydantic.
- Код структурирован по модулям, что упрощает поддержку.
