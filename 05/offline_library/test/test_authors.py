import pytest

from ..src.app.schemas import AuthorCreate, AuthorUpdate, AuthorDB
from ..src.app.crud import create_author, get_author


@pytest.mark.create
@pytest.mark.author
async def test_create_author(client):
    data = {
        "name": "Александр Пушкин",
        "bio": "Русский писатель"
    }
    response = client.post("/authors/", json=data)
    assert response.status_code == 201
    author = response.json()
    assert author["name"] == data["name"]
    assert "id" in author


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"name": 123}, "name must be a string"),
        ({"bio": None}, "bio is optional"),
        ({}, "name is required")
    ]
)
@pytest.mark.validation
@pytest.mark.author
async def test_invalid_create_author(client, invalid_data, expected_error):
    response = client.post("/authors/", json=invalid_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert expected_error in str(errors)


@pytest.mark.read
@pytest.mark.author
async def test_get_authors(client):
    # Создаем автора внутри теста
    create_resp = client.post("/authors/", json={"name": "Л. Толстой", "bio": ""})
    author_id = create_resp.json()["id"]

    response = client.get("/authors/")
    assert response.status_code == 200
    authors = response.json()
    assert len(authors) == 1
    assert authors[0]["name"] == "Л. Толстой"


# Добавьте эти тесты в ваш файл

@pytest.mark.update
@pytest.mark.author
async def test_update_author(client):
    """Проверка обновления существующего автора"""
    # Создаём автора
    create_resp = client.post("/authors/", json={"name": "Старый автор", "bio": "Старая биография"})
    author_id = create_resp.json()["id"]

    # Обновляем данные
    update_data = {
        "name": "Обновлённый автор",
        "bio": "Обновлённая биография с новыми деталями"
    }
    response = client.put(f"/authors/{author_id}", json=update_data)

    assert response.status_code == 200
    updated_author = response.json()

    # Проверяем изменения
    assert updated_author["name"] == update_data["name"]
    assert updated_author["bio"] == update_data["bio"]
    assert "id" in updated_author


@pytest.mark.read
@pytest.mark.author
async def test_get_single_author(client):
    """Получение конкретного автора по ID"""
    create_resp = client.post("/authors/", json={"name": "Лев Толстой", "bio": ""})
    author_id = create_resp.json()["id"]

    response = client.get(f"/authors/{author_id}")
    assert response.status_code == 200
    author = response.json()

    assert author["name"] == "Лев Толстой"
    assert author["id"] == author_id


@pytest.mark.delete
@pytest.mark.cascade
@pytest.mark.author
async def test_delete_author_with_books(client):
    """Каскадное удаление автора и связанных книг"""
    # Создаём автора
    author_resp = client.post("/authors/", json={"name": "Каскадный автор", "bio": "Для теста"})
    author_id = author_resp.json()["id"]

    # Создаём книгу
    book_resp = client.post("/books/", json={
        "title": "Каскадная книга",
        "author_id": author_id,
        "year": 2025,
        "pages": 250
    })
    book_id = book_resp.json()["id"]

    # Удаляем автора
    delete_resp = client.delete(f"/authors/{author_id}")
    assert delete_resp.status_code == 200

    # Проверяем удаление книги
    book_check = client.get(f"/books/{book_id}")
    assert book_check.status_code == 404  # Книга должна быть удалена


@pytest.mark.parametrize(
    "long_data, max_length, field",
    [
        ({"name": "a" * 101}, 100, "name"),  # Превышение лимита для name (String(100))
        ({"bio": "b" * 501}, 500, "bio")  # Превышение лимита для bio (String(500))
    ]
)
@pytest.mark.validation
@pytest.mark.author
async def test_author_field_length_validation(client, long_data, max_length, field):
    """Проверка ограничений на длину полей"""
    response = client.post("/authors/", json=long_data)
    assert response.status_code == 422

    error_msg = f"ensure this value has at most {max_length} characters"
    errors = response.json()["detail"]
    assert any(error_msg in str(e) for e in errors)
    assert any(field in str(e) for e in errors)


@pytest.mark.read
@pytest.mark.author
async def test_get_nonexistent_author(client):
    """Получение несуществующего автора"""
    response = client.get("/authors/99999")
    assert response.status_code == 404
    assert "Author not found" in response.json()["detail"]


@pytest.mark.update
@pytest.mark.author
async def test_partial_update_author(client):
    """Частичное обновление (только одного поля)"""
    create_resp = client.post("/authors/", json={"name": "Частичный автор", "bio": "Исходная биография"})
    author_id = create_resp.json()["id"]

    # Обновляем только биографию
    response = client.patch(f"/authors/{author_id}", json={"bio": "Обновлённая биография"})
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == "Частичный автор"  # Имя не менялось
    assert updated["bio"] == "Обновлённая биография"
