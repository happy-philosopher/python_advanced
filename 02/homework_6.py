# 6. Обработка ошибок.
# Создайте корутину safe_fetch(url), которая: пытается получить данные с указанного URL,
# обрабатывает возможные ошибки (сетевые, HTTP-ошибки), возвращает данные или None в случае ошибки.
# Протестируйте на корректном и некорректном URL.


import aiohttp
import asyncio


async def safe_fetch(url):
    """
    Асинхронно получает данные с указанного URL.
    Обрабатывает сетевые ошибки, HTTP‑ошибки и другие исключения.
    Возвращает данные (JSON) или None в случае ошибки.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                # Проверяем HTTP‑статус: считаем успешными коды 200–299
                if 200 <= response.status < 300:
                    # Пытаемся распарсить JSON
                    data = await response.json()
                    return data
                else:
                    print(f"HTTP-ошибка: статус {response.status} для URL: {url}")
                    return None
    except aiohttp.ClientError as e:
        # Ошибки клиента aiohttp: проблемы с подключением, DNS, таймаут и т.д.
        print(f"Сетевая ошибка (aiohttp): {e} для URL: {url}")
        return None
    except asyncio.TimeoutError:
        # Таймаут асинхронной операции
        print(f"Таймаут операции для URL: {url}")
        return None
    except ValueError as e:
        # Ошибка парсинга JSON (некорректный формат)
        print(f"Ошибка парсинга JSON: {e} для URL: {url}")
        return None
    except Exception as e:
        # Любые другие непредвиденные ошибки
        print(f"Непредвиденная ошибка: {e} для URL: {url}")
        return None


async def test_safe_fetch():
    # Тестовый список URL: один корректный, два некорректных
    urls = [
        "https://jsonplaceholder.typicode.com/users/1",  # Корректный URL
        "https://invalid-domain-example.com/api/data",      # Некорректный домен
        "https://jsonplaceholder.typicode.com/nonexistent"   # Корректный домен, но неверный путь
    ]

    for i, url in enumerate(urls, 1):
        print(f"\n--- Тест {i}: {url} ---")
        result = await safe_fetch(url)

        if result is not None:
            print("Данные успешно получены:")
            print(result)
        else:
            print("Не удалось получить данные (возвращено None)")


# Запуск теста
asyncio.run(test_safe_fetch())
