import pytest
from datetime import date

from ..src.app.schemas import ClientCreate, ClientUpdate, ClientDB
from ..src.app.crud import create_client, get_client


@pytest.mark.create
@pytest.mark.client
async def test_create_client(client):
    data = {
        "full_name": "Иван Петров",
        "phone": "+79991234567",
        "email": "ivan@test.ru"
    }

    response = client.post("/clients/", json=data)
    assert response.status_code == 201
    client_data = response.json()
    assert client_data["full_name"] == data["full_name"]
    assert client_data["phone"] == data["phone"]
    assert client_data["email"] == data["email"]
    assert "id" in client_data


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"full_name": "", "phone": "+79991234567", "email": "ivan@test.ru"}, "full_name must not be empty"),
        ({"full_name": "Иван Петров", "phone": "", "email": "ivan@test.ru"}, "phone must not be empty"),
        ({"full_name": "Иван Петров", "phone": "+79991234567", "email": ""}, "email must not be empty"),
        ({"full_name": "Иван Петров", "phone": "12345", "email": "ivan@test.ru"}, "phone must be 15 characters long"),
        ({"full_name": "Иван Петров", "phone": "+79991234567", "email": "invalid_email"}, "email must be valid"),
        ({"full_name": "Иван Петров", "phone": "+79991234567"}, "email is required")
    ]
)
@pytest.mark.validation
@pytest.mark.client
async def test_invalid_create_client(client, invalid_data, expected_error):
    response = client.post("/clients/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert expected_error in str(errors)


@pytest.mark.read
@pytest.mark.client
async def test_get_clients(client):
    # Создаем клиента внутри теста
    create_resp = client.post("/clients/", json={
        "full_name": "Тестовый клиент",
        "phone": "+79991234567",
        "email": "test@test.ru"
    })
    client_id = create_resp.json()["id"]

    response = client.get("/clients/")
    assert response.status_code == 200
    clients = response.json()
    assert len(clients) == 1
    assert clients[0]["full_name"] == "Тестовый клиент"


@pytest.mark.update
@pytest.mark.client
async def test_update_client(client):
    # Создаем клиента
    create_resp = client.post("/clients/", json={
        "full_name": "Старый клиент",
        "phone": "+79991234567",
        "email": "old@test.ru"
    })
    client_id = create_resp.json()["id"]

    update_data = {
        "full_name": "Обновленный клиент",
        "phone": "+79997654321",
        "email": "new@test.ru"
    }

    response = client.put(f"/clients/{client_id}", json=update_data)
    assert response.status_code == 200
    updated_client = response.json()
    assert updated_client["full_name"] == "Обновленный клиент"
    assert updated_client["phone"] == "+79997654321"
    assert updated_client["email"] == "new@test.ru"


@pytest.mark.delete
@pytest.mark.client
async def test_delete_client(client):
    # Создаем клиента
    create_resp = client.post("/clients/", json={
        "full_name": "Тестовый клиент",
        "phone": "+79991234567",
        "email": "test@test.ru"
    })
    client_id = create_resp.json()["id"]

    # Удаляем клиента
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200

    # Проверяем, что клиент удален
    get_resp = client.get(f"/clients/{client_id}")
    assert get_resp.status_code == 404


@pytest.mark.parametrize(
    "email, expected_error",
    [
        ("valid@email.ru", None),  # валидный email
        ("invalid_email", "value is not a valid email address"),
        ("test@", "value is not a valid email address"),
        ("", "email must not be empty"),
        ("a" * 151 + "@test.ru", "ensure this value has at most 150 characters")
    ]
)
@pytest.mark.validation
@pytest.mark.client
async def test_email_validation(client, email, expected_error):
    data = {
        "full_name": "Тестовый клиент",
        "phone": "+79991234567",
        "email": email
    }

    response = client.post("/clients/", json=data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "phone, expected_error",
    [
        ("+79991234567", None),  # валидный телефон
        ("1234567890", "phone must be 15 characters long"),
        ("+7999123456", "phone must be 15 characters long"),
        ("+799912345678", "phone must be 15 characters long"),
        ("", "phone must not be empty"),
        ("abcdefghij", "phone must contain only digits")
    ]
)
@pytest.mark.validation
@pytest.mark.client
async def test_phone_validation(client, phone, expected_error):
    data = {
        "full_name": "Тестовый клиент",
        "phone": phone,
        "email": "test@test.ru"
    }

    response = client.post("/clients/", json=data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "full_name_length, expected_error",
    [
        (150, None),  # валидная длина
        (151, "ensure this value has at most 150 characters"),
        (1, None),  # минимальная длина
        (0, "value error")  # пустое значение
    ]
)
@pytest.mark.validation
@pytest.mark.client
async def test_full_name_validation(client, full_name_length, expected_error):
    if full_name_length == 0:
        full_name = ""
    else:
        full_name = "a" * full_name_length

    data = {
        "full_name": full_name,
        "phone": "+79991234567",
        "email": "test@test.ru"
    }

    response = client.post("/clients/", json=data)

    if expected_error:
        assert response.status_code == 42
