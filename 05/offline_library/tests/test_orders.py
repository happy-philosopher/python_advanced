import pytest
from datetime import date, timedelta
from src.app.schemas import AuthorCreate, BookCreate, ClientCreate, OrderCreate


@pytest.mark.orders
class TestOrders:
    """Тесты для операций с заказами"""

    @pytest.mark.create
    def test_create_order_success(self, client, db_session):
        """Тест успешного создания заказа"""
        from src.app.crud import create_author, create_book, create_client

        # Создаем необходимые объекты
        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="client@example.com"
        )))

        order_data = {
            "client_id": client_obj.id,
            "book_id": book.id,
            "issue_date": date(2024, 1, 1).isoformat(),
            "return_date": date(2024, 1, 15).isoformat()
        }
        response = client.post("/orders/", json=order_data)

        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_obj.id
        assert data["book_id"] == book.id
        assert data["issue_date"] == order_data["issue_date"]

    @pytest.mark.create
    def test_create_order_null_return(self, client, db_session):
        """Тест создания заказа без даты возврата"""
        from src.app.crud import create_author, create_book, create_client

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="client@example.com"
        )))

        order_data = {
            "client_id": client_obj.id,
            "book_id": book.id,
            "issue_date": date(2024, 1, 1).isoformat(),
            "return_date": None
        }
        response = client.post("/orders/", json=order_data)

        assert response.status_code == 200
        data = response.json()
        assert data["return_date"] is None

    @pytest.mark.read
    def test_get_order_success(self, client, db_session):
        """Тест успешного получения заказа"""
        from src.app.crud import create_author, create_book, create_client, create_order

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="client@example.com"
        )))

        order_data = OrderCreate(
            client_id=client_obj.id,
            book_id=book.id,
            issue_date=date(2024, 1, 1),
            return_date=date(2024, 1, 15)
        )
        order = pytest.asyncio.run(create_order(db_session, order_data))

        response = client.get(f"/orders/{order.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order.id
        assert data["client_id"] == client_obj.id
        assert data["book_id"] == book.id

    @pytest.mark.read
    def test_get_order_not_found(self, client):
        """Тест получения несуществующего заказа"""
        response = client.get("/orders/99999")
        assert response.status_code == 404

    @pytest.mark.update
    def test_update_order_success(self, client, db_session):
        """Тест успешного обновления заказа"""
        from src.app.crud import create_author, create_book, create_client, create_order

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="client@example.com"
        )))

        order_data = OrderCreate(
            client_id=client_obj.id,
            book_id=book.id,
            issue_date=date(2024, 1, 1),
            return_date=date(2024, 1, 15)
        )
        order = pytest.asyncio.run(create_order(db_session, order_data))

        new_return_date = date(2024, 2, 1).isoformat()
        update_data = {
            "return_date": new_return_date
        }
        response = client.put(f"/orders/{order.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["return_date"] == new_return_date

    @pytest.mark.delete
    def test_delete_order_success(self, client, db_session):
        """Тест успешного удаления заказа"""
        from src.app.crud import create_author, create_book, create_client, create_order

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email="client@example.com"
        )))

        order_data = OrderCreate(
            client_id=client_obj.id,
            book_id=book.id,
            issue_date=date(2024, 1, 1),
            return_date=date(2024, 1, 15)
        )
        order = pytest.asyncio.run(create_order(db_session, order_data))

        response = client.delete(f"/orders/{order.id}")
        assert response.status_code == 200
        assert response.json() is True

        # Проверяем, что заказ удален
        get_response = client.get(f"/orders/{order.id}")
        assert get_response.status_code == 404

    @pytest.mark.parametrize("days_to_return", [
        1, 7, 14, 30
    ])
    @pytest.mark.create
    def test_create_orders_parametrized(self, client, db_session, days_to_return):
        """Параметризованный тест создания заказов с разными сроками"""
        from src.app.crud import create_author, create_book, create_client, create_order

        author = pytest.asyncio.run(create_author(db_session, AuthorCreate(name="Автор", bio="Био")))
        book = pytest.asyncio.run(create_book(db_session, BookCreate(
            title="Книга", author_id=author.id, year=2024, pages=100
        )))
        client_obj = pytest.asyncio.run(create_client(db_session, ClientCreate(
            full_name="Клиент", phone="+79111234567", email=f"client_{days_to_return}@example.com"
        )))

        issue_date = date(2024, 1, 1)
        return_date = issue_date + timedelta(days=days_to_return)

        order_data = {
            "client_id": client_obj.id,
            "book_id": book.id,
            "issue_date": issue_date.isoformat(),
            "return_date": return_date.isoformat()
        }
        response = client.post("/orders/", json=order_data)

        assert response.status_code == 200
        data = response.json()
        assert data["return_date"] == return_date.isoformat()
