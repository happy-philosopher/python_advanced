# Е1. Менеджер загрузок.
# Создайте асинхронный менеджер загрузки файлов.
# Функция download_manager(urls, max_concurrent=5): принимает список URL для загрузки,
# ограничивает количество одновременных загрузок (используйте asyncio.Semaphore),
# показывает прогресс загрузки каждого файла, обрабатывает ошибки и повторяет неудачные загрузки.
# Используйте для тестирования несколько эндпоинтов JSONPlaceholder.
# Добавьте возможность отмены всех загрузок (cancel tasks).


import asyncio
import aiohttp
import json


async def download_file(semaphore, session, url, max_attempts=3):
    """Загружает файл с повторными попытками и ограничением параллелизма."""
    async with semaphore:
        for attempt in range(max_attempts):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()  # Вызывает исключение для статусов ≥400
                    content = await response.text()
                    print(f"Успешно загружен {url} (попытка {attempt + 1})")
                    return content
            except aiohttp.ClientError as e:
                print(f"Клиентская ошибка для {url} (попытка {attempt + 1}): {e}")
            except asyncio.TimeoutError:
                print(f"Таймаут для {url} (попытка {attempt + 1})")
            except Exception as e:
                print(f"Неожиданная ошибка для {url} (попытка {attempt + 1}): {e}")
            if attempt == max_attempts - 1:
                print(f"Не удалось загрузить {url} после {max_attempts} попыток")
        return None


async def download_manager(urls, max_concurrent=5):
    """Менеджер загрузок с ограничением параллельных задач и возможностью отмены."""
    semaphore = asyncio.Semaphore(max_concurrent)
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(download_file(semaphore, session, url))
            for url in urls
        ]
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            print("Менеджер загрузок отменён")
            for task in tasks:
                task.cancel()
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                pass
        return results


# Тестирование с JSONPlaceholder
async def test_download_manager():
    urls = [
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://jsonplaceholder.typicode.com/comments/1',
        'https://jsonplaceholder.typicode.com/albums/1',
        'https://jsonplaceholder.typicode.com/photos/1',  # пример изображения
        'https://jsonplaceholder.typicode.com/todos/1',
        'https://jsonplaceholder.typicode.com/invalid'  # намеренная ошибка
    ]

    # Запуск менеджера
    manager_task = asyncio.create_task(download_manager(urls, max_concurrent=3))

    # Имитация отмены через 2 секунды
    await asyncio.sleep(2)
    manager_task.cancel()

    try:
        results = await manager_task
        print("\nРезультаты:")
        for i, result in enumerate(results, 1):
            if result is None:
                print(f"Загрузка {i}: Не удалось")
                continue
            try:
                # Распарсить JSON
                data = json.loads(result)
                # Отформатировать с отступами
                pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
                print(f"\nЗагрузка {i}:\n{pretty_json}")
            except json.JSONDecodeError:
                print(f"Загрузка {i}: Некорректный JSON: {result}")
    except asyncio.CancelledError:
        print("Задача менеджера была отменена")


# Запуск теста
asyncio.run(test_download_manager())


