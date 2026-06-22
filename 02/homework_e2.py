# Е2. Система мониторинга API:
# - Создайте систему мониторинга доступности API.
# - Периодически (каждые 5 секунд) проверяйте доступность нескольких эндпоинтов. Найдите для этого несколько
# публичных API, которые можете использовать в работе.
# - Измеряйте время отклика каждого эндпоинта.
# - Ведите статистику: успешные/неуспешные запросы, среднее время отклика.
# - Используйте asyncio.create_task для фоновых задач.
# - Программа должна работать заданное количество секунд.
# - При остановке выведите финальную статистику.


import asyncio
import aiohttp
import time


async def check_endpoint(session, url, stats):
    """Проверяет доступность эндпоинта, измеряет время отклика и обновляет статистику."""
    start_time = time.perf_counter()
    try:
        async with session.get(url) as response:
            elapsed = time.perf_counter() - start_time
            stats[url]['total_time'] += elapsed
            stats[url]['count'] += 1
            if response.status == 200:
                stats[url]['success'] += 1
            else:
                stats[url]['failure'] += 1
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        stats[url]['total_time'] += elapsed
        stats[url]['count'] += 1
        stats[url]['failure'] += 1


async def monitor_endpoints(session, endpoints, stats, duration):
    """Периодически (каждые 5 сек) проверяет все эндпоинты."""
    end_time = time.monotonic() + duration
    while time.monotonic() < end_time:
        tasks = [asyncio.create_task(check_endpoint(session, url, stats)) for url in endpoints]
        await asyncio.gather(*tasks)  # Дожидаемся завершения всех запросов
        await asyncio.sleep(5)  # Ждем 5 секунд перед следующей проверкой


async def main():
    # Выбираем публичные API для мониторинга
    endpoints = [
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://jsonplaceholder.typicode.com/comments/1',
        'https://jsonplaceholder.typicode.com/albums/1'
    ]

    # Инициализируем статистику
    stats = {url: {'success': 0, 'failure': 0, 'total_time': 0.0, 'count': 0} for url in endpoints}

    # Запрашиваем длительность работы
    duration = int(input("Введите длительность мониторинга (в секундах): "))

    async with aiohttp.ClientSession() as session:
        await monitor_endpoints(session, endpoints, stats, duration)

    # Выводим итоговую статистику
    print("\nИтоговая статистика:")
    for url in endpoints:
        data = stats[url]
        total_requests = data['count']
        if total_requests == 0:
            print(f"{url}: Запросы не выполнялись")
            continue

        success_rate = (data['success'] / total_requests) * 100
        failure_rate = (data['failure'] / total_requests) * 100
        avg_response_time = data['total_time'] / total_requests

        print(f"Эндпоинт: {url}")
        print(f"  Всего запросов: {total_requests}")
        print(f"  Успешных: {data['success']} ({success_rate:.2f}%)")
        print(f"  Неуспешных: {data['failure']} ({failure_rate:.2f}%)")
        print(f"  Среднее время отклика: {avg_response_time:.3f} сек\n")


# Запуск
asyncio.run(main())
