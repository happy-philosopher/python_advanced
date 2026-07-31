import pytest
from datetime import date

from ..src.app.schemas import BookCreate, BookUpdate, BookDB
from ..src.app.crud import create_book, get_book
from ..src.app.schemas import AuthorCreate


@pytest.mark.create
@pytest.mark.book
async def test_create_book(client):
    # Сначала создаем автора, так как книга связана с автором
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    book_data = {
        "title": "Новая книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    }

    response = client.post("/books/", json=book_data)
    assert response.status_code == 201
    book = response.json()
    assert book["title"] == book_data["title"]
    assert book["year"] == book_data["year"]
    assert book["pages"] == book_data["pages"]
    assert book["author_id"] == author_id


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"title": 123}, "title must be a string"),
        ({"year": "2026"}, "year must be an integer"),
        ({"pages": "300"}, "pages must be an integer"),
        ({"author_id": "abc"}, "author_id must be an integer"),
        ({}, "title is required"),
        ({"title": "Книга", "year": 2026, "pages": 300}, "author_id is required")
    ]
)
@pytest.mark.validation
@pytest.mark.book
async def test_invalid_create_book(client, invalid_data, expected_error):
    response = client.post("/books/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert expected_error in str(errors)


@pytest.mark.read
@pytest.mark.book
async def test_get_books(client):
    # Создаем книгу внутри теста
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    create_resp = client.post("/books/", json={
        "title": "Тестовая книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })

    response = client.get("/books/")
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]["title"] == "Тестовая книга"


@pytest.mark.update
@pytest.mark.book
async def test_update_book(client):
    # Создаем автора и книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    create_resp = client.post("/books/", json={
        "title": "Старая книга",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = create_resp.json()["id"]

    update_data = {
        "title": "Обновленная книга",
        "year": 2027
    }

    response = client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 200
    updated_book = response.json()
    assert updated_book["title"] == "Обновленная книга"
    assert updated_book["year"] == 2027
    assert updated_book["pages"] == 300  # Неизмененное поле


@pytest.mark.delete
@pytest.mark.book
async def test_delete_book(client):
    # Создаем автора и книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    create_resp = client.post("/books/", json={
        "title": "Книга для удаления",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = create_resp.json()["id"]

    # Удаляем книгу
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200

    # Проверяем, что книга удалена
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


@pytest.mark.parametrize(
    "year, expected_error",
    [
        (2026, None),  # валидное значение
        (0, "year must be greater than 0"),
        (-100, "year must be greater than 0"),
        (99999, "year must be reasonable")
    ]
)
@pytest.mark.validation
@pytest.mark.book
async def test_year_validation(client, year, expected_error):
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    data = {
        "title": "Тестовая книга",
        "author_id": author_id,
        "year": year,
        "pages": 300
    }

    response = client.post("/books/", json=data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "pages, expected_error",
    [
        (300, None),  # валидное значение
        (0, "pages must be greater than 0"),
        (-10, "pages must be greater than 0"),
        (1000000, "pages must be reasonable")
    ]
)
@pytest.mark.validation
@pytest.mark.book
async def test_pages_validation(client, pages, expected_error):
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    data = {
        "title": "Тестовая книга",
        "author_id": author_id,
        "year": 2026,
        "pages": pages
    }

    response = client.post("/books/", json=data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.parametrize(
    "title_length, expected_error",
    [
        (200, None),  # валидное значение
        (201, "ensure this value has at most 200 characters"),
        (1, None),  # минимальная длина
        (0, "value error")  # пустое значение
    ]
)
@pytest.mark.validation
@pytest.mark.book
async def test_title_length_validation(client, title_length, expected_error):
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    if title_length == 0:
        title = ""
    else:
        title = "a" * title_length

    data = {
        "title": title,
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    }

    response = client.post("/books/", json=data)

    if expected_error:
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert expected_error in str(errors)
    else:
        assert response.status_code == 201


@pytest.mark.delete
@pytest.mark.book
async def test_delete_book_cascade(client):
    # Создаем автора и книгу
    author_resp = client.post("/authors/", json={
        "name": "Автор для теста",
        "bio": "Био автора"
    })
    author_id = author_resp.json()["id"]

    create_resp = client.post("/books/", json={
        "title": "Книга для удаления",
        "author_id": author_id,
        "year": 2026,
        "pages": 300
    })
    book_id = create_resp.json()["id"]

    # Создаем заказ на эту книгу
    client_resp = client.post("/clients/", json={
        "full_name": "Клиент",
        "phone": "1234567890",
        "email": "client@test.ru"
    })
    client_id = client_resp.json()["id"]

    order_resp = client.post("/orders/", json={
        "client_id": client_id,
        "book_id": book_id,
        "issue_date": "2026-07-27"
    })

    # Удаляем книгу
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200

    # Проверяем, что книга и заказ удалены
    get_book_resp = client.get(f"/books/{book_id}")
    assert get_book_resp.status_code == 404

    get_order_resp = client.get(f"/orders/")
    orders = get_order_resp.json()
    assert not any(order["book_id"] == book_id for order in orders)
