import pytest
from src.app.schemas import ClientCreate


@pytest.mark.clients
class TestClients:
    """Тесты для операций с клиентами"""

    @pytest.mark.create
    def test_create_client_success(self, client):
        """Тест успешного создания клиента"""
        client_data = {
            "full_name": "Иван Иванов",
            "phone": "+79111234567",
            "email": "ivan@example.com"
        }
        response = client.post("/clients/", json=client_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == client_data["full_name"]
        assert data["phone"] == client_data["phone"]
        assert data["email"] == client_data["email"]

    @pytest.mark.create
    @pytest.mark.validation
    def test_create_client_duplicate_email(self, client, db_session):
        """Тест создания клиента с существующим email"""
        from src.app.crud import create_client

        # Создаем первого клиента
        client_data = ClientCreate(
            full_name="Первый Клиент",
            phone="+79111234567",
            email="duplicate@example.com"
        )
        pytest.asyncio.run(create_client(db_session, client_data))

        # Пытаемся создать второго с тем же email
        duplicate_data = {
            "full_name": "Второй Клиент",
            "phone": "+79221234567",
            "email": "duplicate@example.com"
        }
        response = client.post("/clients/", json=duplicate_data)
        # Должна быть ошибка уникальности (500 или 422)
        assert response.status_code in [500, 422]

    @pytest.mark.read
    def test_get_client_success(self, client, db_session):
        """Тест успешного получения клиента"""
        from src.app.crud import create_client

        client_data = ClientCreate(
            full_name="Тестовый Клиент",
            phone="+79111234567",
            email="test@example.com"
        )
        client_obj = pytest.asyncio.run(create_client(db_session, client_data))

        response = client.get(f"/clients/{client_obj.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Тестовый Клиент"
        assert data["email"] == "test@example.com"

    @pytest.mark.read
    def test_get_client_not_found(self, client):
        """Тест получения несуществующего клиента"""
        response = client.get("/clients/99999")
        assert response.status_code == 404

    @pytest.mark.update
    def test_update_client_success(self, client, db_session):
        """Тест успешного обновления клиента"""
        from src.app.crud import create_client

        client_data = ClientCreate(
            full_name="Исходный Клиент",
            phone="+79111234567",
            email="original@example.com"
        )
        client_obj = pytest.asyncio.run(create_client(db_session, client_data))

        update_data = {
            "full_name": "Обновленный Клиент",
            "phone": "+79221234567"
        }
        response = client.put(f"/clients/{client_obj.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone"] == update_data["phone"]
        assert data["email"] == "original@example.com"  # Не изменился

    @pytest.mark.delete
    def test_delete_client_success(self, client, db_session):
        """Тест успешного удаления клиента"""
        from src.app.crud import create_client

        client_data = ClientCreate(
            full_name="Клиент для удаления",
            phone="+79111234567",
            email="delete@example.com"
        )
        client_obj = pytest.asyncio.run(create_client(db_session, client_data))

        response = client.delete(f"/clients/{client_obj.id}")
        assert response.status_code == 200
        assert response.json() is True

        # Проверяем, что клиент удален
        get_response = client.get(f"/clients/{client_obj.id}")
        assert get_response.status_code == 404

    @pytest.mark.parametrize("full_name,phone,email", [
        ("Клиент 1", "+71111111111", "client1@example.com"),
        ("Клиент 2", "+72222222222", "client2@example.com"),
        ("Клиент 3", "+73333333333", "client3@example.com"),
    ])
    @pytest.mark.create
    def test_create_clients_parametrized(self, client, full_name, phone, email):
        """Параметризованный тест создания клиентов"""
        client_data = {
            "full_name": full_name,
            "phone": phone,
            "email": email
        }
        response = client.post("/clients/", json=client_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == full_name
        assert data["phone"] == phone
        assert data["email"] == email
