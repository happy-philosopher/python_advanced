# Pydantic-модели для валидации (app/schemas.py)


from pydantic import BaseModel
from datetime import date


# Автор
class AuthorCreate(BaseModel):
    name: str
    bio: str | None = None

class AuthorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None

class AuthorDB(BaseModel):
    id: int
    name: str
    bio: str | None


# Книга
class BookCreate(BaseModel):
    title: str
    author_id: int
    year: int
    pages: int

class BookUpdate(BaseModel):
    title: str | None = None
    author_id: int | None = None
    year: int | None = None
    pages: int | None = None

class BookDB(BaseModel):
    id: int
    title: str
    author_id: int
    year: int
    pages: int


# Клиент
class ClientCreate(BaseModel):
    full_name: str
    phone: str
    email: str

class ClientUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None

class ClientDB(BaseModel):
    id: int
    full_name: str
    phone: str
    email: str


# Заказ
class OrderCreate(BaseModel):
    client_id: int
    book_id: int
    issue_date: date
    return_date: date | None = None

class OrderUpdate(BaseModel):
    client_id: int | None = None
    book_id: int | None = None
    issue_date: date | None = None
    return_date: date | None = None

class OrderDB(BaseModel):
    id: int
    client_id: int
    book_id: int
    issue_date: date
    return_date: date | None = None
