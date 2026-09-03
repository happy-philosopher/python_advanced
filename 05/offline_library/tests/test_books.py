import pytest
from src.app.schemas import AuthorCreate, BookCreate


@pytest.mark.books
class TestBooks:
    """Тесты для операций с книгами"""

    @pytest.mark.create
    def test_create_book_success(self, client, db_session):
        """Тест успешного создания книги"""
        from src.app.crud import create_author

        # Создаем автора
        author_data = AuthorCreate(name="Тестовый Автор", bio="Биография")
        author = pytest.asyncio.run(create_author(db_session, author_data))

        book_data = {
            "title": "Война и мир",
            "author_id": author.id,
            "year": 1869,
            "pages": 1225
        }
        response = client.post("/books/", json=book_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == book_data["title"]
        assert data["author_id"] == author.id
        assert data["year"] == book_data["year"]
        assert data["pages"] == book_data["pages"]

    @pytest.mark.create
    @pytest.mark.validation
    def test_create_book_invalid_author(self, client, db_session):
        """Тест создания книги с несуществующим автором"""
        # Создаем книгу с несуществующим author_id
        book_data = {
            "title": "Книга без автора",
            "author_id": 99999,
            "year": 2024,
            "pages": 100
        }
        response = client.post("/books/", json=book_data)
        # В зависимости от реализации может быть 500 или 422
        assert response.status_code in [500, 422]

    @pytest.mark.read
    def test_get_book_success(self, client, db_session):
        """Тест успешного получения книги"""
        from src.app.crud import create_author, create_book

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book_data = BookCreate(title="Книга", author_id=author.id, year=2023, pages=200)
        book = pytest.asyncio.run(create_book(db_session, book_data))

        response = client.get(f"/books/{book.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Книга"
        assert data["author_id"] == author.id

    @pytest.mark.read
    def test_get_book_not_found(self, client):
        """Тест получения несуществующей книги"""
        response = client.get("/books/99999")
        assert response.status_code == 404

    @pytest.mark.read
    def test_get_books_list(self, client, db_session):
        """Тест получения списка книг"""
        from src.app.crud import create_author, create_book

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))

        # Создаем несколько книг
        books_data = [
            BookCreate(title="Книга 1", author_id=author.id, year=2023, pages=100),
            BookCreate(title="Книга 2", author_id=author.id, year=2023, pages=200),
        ]
        for book_data in books_data:
            pytest.asyncio.run(create_book(db_session, book_data))

        response = client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    @pytest.mark.update
    def test_update_book_success(self, client, db_session):
        """Тест успешного обновления книги"""
        from src.app.crud import create_author, create_book

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book_data = BookCreate(title="Исходная книга", author_id=author.id, year=2023, pages=100)
        book = pytest.asyncio.run(create_book(db_session, book_data))

        update_data = {
            "title": "Обновленная книга",
            "pages": 150
        }
        response = client.put(f"/books/{book.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["pages"] == update_data["pages"]
        assert data["year"] == 2023  # Не изменялось

    @pytest.mark.delete
    def test_delete_book_success(self, client, db_session):
        """Тест успешного удаления книги"""
        from src.app.crud import create_author, create_book

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book_data = BookCreate(title="Книга для удаления", author_id=author.id, year=2023, pages=100)
        book = pytest.asyncio.run(create_book(db_session, book_data))

        response = client.delete(f"/books/{book.id}")
        assert response.status_code == 200
        assert response.json() is True

        # Проверяем, что книга удалена
        get_response = client.get(f"/books/{book.id}")
        assert get_response.status_code == 404

    @pytest.mark.parametrize("title,year,pages", [
        ("Книга 1", 2020, 150),
        ("Книга 2", 2021, 200),
        ("Книга 3", 2022, 250),
    ])
    @pytest.mark.create
    def test_create_books_parametrized(self, client, db_session, title, year, pages):
        """Параметризованный тест создания книг"""
        from src.app.crud import create_author

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))

        book_data = {
            "title": title,
            "author_id": author.id,
            "year": year,
            "pages": pages
        }
        response = client.post("/books/", json=book_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == title
        assert data["year"] == year
        assert data["pages"] == pages
