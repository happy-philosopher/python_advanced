# Добавьте POST эндпойнт /books, который принимает модель Book и возвращает её с добавленным полем id.


from typing import Optional, List
from fastapi import FastAPI, status
from pydantic import BaseModel, Field, field_validator


app = FastAPI()


class Book(BaseModel):
    title: str
    author: str
    pages: int = Field(ge=1, description="Количество страниц, минимум 1")
    isbn: Optional[str] = None

    @field_validator("isbn", mode="before")
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None

        # Убираем пробелы и дефисы
        cleaned = "".join(ch for ch in v if ch not in "- ")

        if not cleaned:
            raise ValueError("ISBN не может состоять только из разделителей")

        # Простая проверка: 10 или 13 символов, цифры и X (только в конце для 10)
        if len(cleaned) == 10 and cleaned[:-1].isdigit() and (cleaned[-1].isdigit() or cleaned[-1].upper() == "X"):
            return cleaned
        if len(cleaned) == 13 and cleaned.isdigit():
            return cleaned

        raise ValueError(
            f"Некорректный ISBN: '{v}'. "
            "Должен быть 10 или 13 символов (допускаются цифры и X в конце для ISBN‑10)."
        )


class BookWithId(Book):
    id: int


MOCK_BOOKS = [
    {"title": "Преступление и наказание", "author": "Фёдор Достоевский", "pages": 672, "isbn": "978-5-17-090630-7"},
    {"title": "Война и мир", "author": "Лев Толстой", "pages": 1274, "isbn": "978-5-17-113383-5"},
    {"title": "Мастер и Маргарита", "author": "Михаил Булгаков", "pages": 528, "isbn": "978-5-17-145797-1"},
    {"title": "Тихий Дон", "author": "Михаил Шолохов", "pages": 1504, "isbn": "978-5-17-136583-2"},
    {"title": "Анна Каренина", "author": "Лев Толстой", "pages": 864, "isbn": "978-5-17-121329-7"},
]

_books_db: List[BookWithId] = []
_next_id = 1

for mock in MOCK_BOOKS:
    book = Book(**mock)  # Теперь это сработает
    book_with_id = BookWithId(**book.model_dump(), id=_next_id)
    _books_db.append(book_with_id)
    _next_id += 1


@app.post("/books", response_model=BookWithId, status_code=status.HTTP_201_CREATED)
def create_book(book: Book) -> BookWithId:
    global _next_id
    book_with_id = BookWithId(**book.model_dump(), id=_next_id)
    _books_db.append(book_with_id)
    _next_id += 1
    return book_with_id


@app.get("/books", response_model=List[BookWithId])
def list_books() -> List[BookWithId]:
    return _books_db
