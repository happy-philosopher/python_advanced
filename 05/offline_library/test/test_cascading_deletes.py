import pytest


@pytest.mark.delete
@pytest.mark.cascade
async def test_delete_author_cascade(client):
    # Создаем автора с книгами
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    # Создаем книги
    book1_resp = client.post("/books/", json={
        "title": "Книга 1",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book1_id = book1_resp.json()["id"]

    book2_resp = client.post("/books/", json={
        "title": "Книга 2",
        "author_id": author_id,
        "year": 2026,
        "pages": 400
    })
    book2_id = book2_resp.json()["id"]

    # Удаляем автора
    response = client.delete(f"/authors/{author_id}")
    assert response.status_code == 200

    # Проверяем удаление книг
    get_book1 = client.get(f"/books/{book1_id}")
    assert get_book1.status_code == 404

    get_book2 = client.get(f"/books/{book2_id}")
    assert get_book2.status_code == 404


@pytest.mark.delete
@pytest.mark.cascade
async def test_delete_client_cascade(client):
    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем заказы
    author_resp = client.post("/authors/", json={
        "name": "Автор",
        "bio": "Био"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = order_resp.json()["id"]

    # Удаляем клиента
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200

    # Проверяем удаление заказов
    get_order = client.get(f"/orders/{order_id}")
    assert get_order.status_code == 404


@pytest.mark.validation
@pytest.mark.order
async def test_unique_book_borrowing(client):
    # Создаем книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор",
        "bio": "Био"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Уникальная книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем клиентов
    client1_resp = client.post("/clients/", json={
        "full_name": "Клиент 1",
        "phone": "+79991234567",
        "email": "client1@test.ru"
    })
    client1_id = client1_resp.json()["id"]

    client2_resp = client.post("/clients/", json={
        "full_name": "Клиент 2",
        "phone": "+79997654321",
        "email": "client2@test.ru"
    })
    client2_id = client2_resp.json()["id"]

    # Первый клиент берет книгу
    order1_resp = client.post("/orders/", json={
        "client_id": client1_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    assert order1_resp.status_code == 201

    # Второй клиент пытается взять ту же книгу
    order2_resp = client.post("/orders/", json={
        "client_id": client2_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    assert order2_resp.status_code == 400
    assert "Книга уже выдана" in order2_resp.json()["detail"]


@pytest.mark.validation
@pytest.mark.order
async def test_return_book(client):
    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор",
        "bio": "Био"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Возвращаемая книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем заказ
    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = order_resp.json()["id"]

    # Обновляем заказ с датой возврата
    update_resp = client.put(f"/orders/{order_id}", json={
        "return_date": "2026-08-27"
    })
    assert update_resp.status_code == 200
    updated_order = update_resp.json()
    assert updated_order["return_date"] == "2026-08-27"

    # Теперь другой клиент может взять эту книгу
    new_client_resp = client.post("/clients/", json={
        "full_name": "Новый клиент",
        "phone": "+79997654321",
        "email": "new_client@test.ru"
    })
    new_client_id = new_client_resp.json()["id"]

    new_order_resp = client.post("/orders/", json={
        "client_id": new_client_id,
        "book_id": book_id,
        "issue_date": "2026-08-28"
    })
    assert new_order_resp.status_code == 201


@pytest.mark.delete
@pytest.mark.cascade
async def test_cascade_delete_author(client):
    # Создаем автора с книгами
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    # Создаем книги
    book1_resp = client.post("/books/", json={
        "title": "Книга 1",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book1_id = book1_resp.json()["id"]

    book2_resp = client.post("/books/", json={
        "title": "Книга 2",
        "author_id": author_id,
        "year": 2026,
        "pages": 400
    })
    book2_id = book2_resp.json()["id"]

    # Создаем заказы на книги
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book1_id,
        "issue_date": "2026-07-27"
    })
    order_id = order_resp.json()["id"]

    # Удаляем автора
    response = client.delete(f"/authors/{author_id}")
    assert response.status_code == 200

    # Проверяем удаление всех связанных сущностей
    # Книги
    get_book1 = client.get(f"/books/{book1_id}")
    assert get_book1.status_code == 404

    get_book2 = client.get(f"/books/{book2_id}")
    assert get_book2.status_code == 404

    # Заказ должен остаться, так как связан с клиентом
    get_order = client.get(f"/orders/{order_id}")
    assert get_order.status_code == 200


@pytest.mark.delete
@pytest.mark.cascade
async def test_cascade_delete_client(client):
    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент для теста",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем книги и заказы
    author_resp = client.post("/authors/", json={
        "name": "Автор",
        "bio": "Био"
    })
    author_id = author_resp.json()["id"]

    book_resp = client.post("/books/", json={
        "title": "Книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = order_resp.json()["id"]

    # Удаляем клиента
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200

    # Проверяем удаление всех заказов клиента
    get_order = client.get(f"/orders/{order_id}")
    assert get_order.status_code == 404

    # Книга должна остаться
    get_book = client.get(f"/books/{book_id}")
    assert get_book.status_code == 200


@pytest.mark.integration
async def test_full_workflow(client):
    # Тестирование полного рабочего процесса

    # Создаем автора
    author_resp = client.post("/authors/", json={
        "name": "Автор",
        "bio": "Био"
    })
    author_id = author_resp.json()["id"]

    # Создаем книгу
    book_resp = client.post("/books/", json={
        "title": "Книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = book_resp.json()["id"]

    # Создаем клиента
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент",
        "phone": "+79991234567",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    # Создаем заказ
    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })
    order_id = order_resp.json()["id"]

    # Обновляем заказ с датой возврата
    update_resp = client.put(f"/orders/{order_id}", json={
        "return_date": "2026-08-27"
    })
    assert update_resp.status_code == 200

    # Проверяем все связи
    assert author_resp.status_code == 201
    assert book_resp.status_code == 201
    assert client_resp.status_code == 201
    assert order_resp.status_code == 201
    assert update_resp.status_code == 200
