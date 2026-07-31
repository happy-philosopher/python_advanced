import pytest
from datetime import date

from ..src.app.schemas import ClientCreate, ClientUpdate, ClientDB
from ..src.app.crud import create_client, get_client


@pytest.mark.create
@pytest.mark.order
async def test_create_order(client):
    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга для теста",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    order_data = {
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    order = response.json()
    assert order["client_id"] == client_id
    assert order["book_id"] == book_id
    assert order["issue_date"] == "2026-07-27"
    assert order["return_date"] is None


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"client_id": 1, "book_id": 1, "issue_date": "2026-07-27"}, None),  # валидный
        ({"client_id": 1, "book_id": 1}, "issue_date is required"),
        ({"book_id": 1, "issue_date": "2026-07-27"}, "client_id is required"),
        ({"client_id": 1, "issue_date": "2026-07-27"}, "book_id is required"),
        ({"client_id": 1, "book_id": 1, "issue_date": "invalid_date"}, "date format error"),
        ({"client_id": "abc", "book_id": 1, "issue_date": "2026-07-27"}, "client_id must be an integer"),
        ({"client_id": 1, "book_id": "abc", "issue_date": "2026-07-27"}, "book_id must be an integer")
    ]
)
@pytest.mark.validation
@pytest.mark.order
async def test_invalid_create_order(client, invalid_data, expected_error):
    response = client.post("/orders/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert expected_error in str(errors)


@pytest.mark.update
@pytest.mark.order
async def test_update_order(client):
    # Создаем необходимые сущности
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга для теста",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем заказ
    create_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = create_resp.json()["id"]

    # Обновляем заказ
    update_data = {
        "return_date": "2026-08-27"
    }

    response = client.put(f"/orders/{order_id}", json=update_data)
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["return_date"] == "2026-08-27"
    assert updated_order["client_id"] == client_id
    assert updated_order["book_id"] == book_id


@pytest.mark.delete
@pytest.mark.order
async def test_delete_order(client):
    # Создаем необходимые сущности
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга для теста",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем заказ
    create_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = create_resp.json()["id"]

    # Удаляем заказ
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200

    # Проверяем удаление
    get_resp = client.get(f"/orders/{order_id}")
    assert get_resp.status_code == 404


@pytest.mark.parametrize(
    "issue_date, return_date, expected_error",
    [
        ("2026-07-27", "2026-08-27", None),  # валидный случай
        ("2026-07-27", "2026-07-26", "return_date must be after issue_date"),
        ("invalid-date", "2026-08-27", "invalid date format"),
        ("2026-07-27", "invalid-date", "invalid date format"),
        (None, "2026-08-27", "issue_date is required"),
        ("2026-07-27", None, "valid case with no return date")
    ]
)
@pytest.mark.validation
@pytest.mark.order
async def test_order_date_validation(client, issue_date, return_date, expected_error):
    # Создаем необходимые сущности
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга для теста",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    order_data = {
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": issue_date,
        "return_date": return_date
    }

    response = client.post("/orders/", json=order_data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "client_id, book_id, expected_error",
    [
        (1, 1, None),  # валидный случай
        (-1, 1, "client not found"),
        (1, -1, "book not found"),
        (0, 1, "client not found"),
        (1, 0, "book not found"),
        ("abc", 1, "client_id must be an integer"),
        (1, "abc", "book_id must be an integer")
    ]
)
@pytest.mark.validation
@pytest.mark.order
async def test_order_foreign_keys_validation(client, client_id, book_id, expected_error):
    order_data = {
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    }

    response = client.post("/orders/", json=order_data)

    if expected_error:
        assert response.status_code == 404
        assert expected_error in response.json()["detail"]
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "book_id, expected_error",
    [
        (1, None),  # валидный случай
        (1, "book already borrowed"),  # попытка взять одну книгу дважды
        (-1, "book not found"),
        (0, "book not found"),
        ("abc", "book_id must be an integer")
    ]
)
@pytest.mark.validation
@pytest.mark.order
async def test_book_availability_validation(client, book_id, expected_error):
    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем заказ на книгу
    first_order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })

    # Пытаемся создать второй заказ на ту же книгу
    second_order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })

    if expected_error:
        assert second_order_resp.status_code == 400
        assert expected_error in second_order_resp.json()["detail"]
    else:
        assert second_order_resp.status_code == 201


@pytest.mark.parametrize(
    "return_date, expected_status",
    [
        ("2026-07-27", 200),  # валидная дата возврата
        ("2026-07-26", 400),  # дата возврата раньше выдачи
        ("invalid-date", 422),  # некорректный формат даты
        (None, 200)  # отсутствие даты возврата
    ]
)
@pytest.mark.update
@pytest.mark.order
async def test_update_return_date(client, return_date, expected_status):
    # Создаем необходимые сущности
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга для теста",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем заказ
    create_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = create_resp.json()["id"]

    # Обновляем дату возврата
    update_data = {
        "return_date": return_date
    }

    response = client.put(f"/orders/{order_id}", json=update_data)
    assert response.status_code == expected_status
