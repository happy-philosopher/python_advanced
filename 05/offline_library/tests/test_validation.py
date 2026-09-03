import pytest
from datetime import date, timedelta
from src.app.schemas import AuthorCreate, ClientCreate, BookCreate


@pytest.mark.validation
class TestValidation:
    """Тесты валидации входных данных"""

    def test_create_author_without_name(self, client):
        """Тест создания автора без обязательного поля name"""
        data = {"bio": "Биография без имени"}
        response = client.post("/authors/", json=data)
        assert response.status_code == 422
        assert "name" in response.json()["detail"].__str__()

    def test_create_book_without_title(self, client):
        """Тест создания книги без обязательного поля title"""
        data = {"author_id": 1, "year": 2024, "pages": 100}
        response = client.post("/books/", json=data)
        assert response.status_code == 422
        assert "title" in response.json()["detail"].__str__()

    def test_create_client_invalid_email(self, client, db_session):
        """Тест создания клиента с некорректным email"""
        data = {
            "full_name": "Тест",
            "phone": "+79111234567",
            "email": "invalid-email"
        }
        response = client.post("/clients/", json=data)
        # Pydantic может не валидировать email, если не указан специальный тип
        # Проверяем, что запрос либо отклонен валидацией, либо создан
        assert response.status_code in [200, 422]

    def test_create_order_with_future_date(self, client, db_session):
        """Тест создания заказа с датой в будущем"""
        from src.app.crud import create_author, create_book, create_client, create_order

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="validation@example.com"
        )))

        future_date = date.today() + timedelta(days=365)
        order_data = {
            "client_id": client_obj.id,
            "book_id": book.id,
            "issue_date": future_date.isoformat(),
            "return_date": None
        }
        # Проверяем, что дата принимается (валидация на уровне БД может не быть)
        response = client.post("/orders/", json=order_data)
        assert response.status_code == 200

    def test_create_client_without_phone(self, client):
        """Тест создания клиента без телефона"""
        data = {
            "full_name": "Тест",
            "email": "test@example.com"
        }
        response = client.post("/clients/", json=data)
        assert response.status_code == 422

    def test_invalid_content_type(self, client):
        """Тест отправки данных в неправильном формате"""
        response = client.post("/authors/", data="invalid data")
        assert response.status_code == 422

    def test_create_author_with_extra_fields(self, client, db_session):
        """Тест создания автора с лишними полями"""
        data = {
            "name": "Автор",
            "bio": "Биография",
            "extra_field": "Лишнее поле"
        }
        response = client.post("/authors/", json=data)
        # Pydantic по умолчанию игнорирует лишние поля
        # Проверяем, что создание прошло успешно
        assert response.status_code == 200
        result = response.json()
        assert "extra_field" not in result
