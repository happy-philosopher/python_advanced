# Создайте Pydantic модель Book с полями: title (обязательное), author
# (обязательное), pages (целое число, минимум 1), isbn (необязательное).


from typing import Optional
from pydantic import BaseModel, Field, field_validator
import isbnlib


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

        # isbnlib.clean убирает пробелы, дефисы и приводит к каноническому виду
        cleaned = isbnlib.clean(v)

        if not cleaned:
            raise ValueError("ISBN не может состоять только из разделителей")

        # Проверяем, что это корректный ISBN‑10 или ISBN‑13 (включая контрольные суммы)
        if isbnlib.is_isbn10(cleaned) or isbnlib.is_isbn13(cleaned):
            # Можно вернуть нормализованный ISBN без дефисов
            return cleaned

        raise ValueError(
            f"Некорректный ISBN: '{v}'. "
            "Убедитесь, что это действительный ISBN‑10 или ISBN‑13 с правильной контрольной цифрой."
        )
