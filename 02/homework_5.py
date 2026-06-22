# 5. Последовательное vs конкурентное выполнение:
# - Создайте функцию get_multiple_users(user_ids).
# - Получите информацию о нескольких пользователях, идентификаторы которых передаются в виде списка.
# - Реализуйте два варианта: последовательный (с await в цикле) и конкурентный (с asyncio.gather).
# - Сравните время выполнения для user_ids = [1, 2, 3, 4, 5].


import aiohttp
import asyncio
import time


async def fetch_user(user_id):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                user_data = await response.json()
                return user_data.get('name')
            else:
                raise Exception(f"Ошибка при запросе: статус {response.status}")


# Последовательное выполнение
async def get_multiple_users_sequential(user_ids):
    users = []
    for user_id in user_ids:
        name = await fetch_user(user_id)
        users.append(name)
    return users


# Конкурентное выполнение
async def get_multiple_users_concurrent(user_ids):
    tasks = [fetch_user(user_id) for user_id in user_ids]
    users = await asyncio.gather(*tasks)
    return users


async def main():
    user_ids = [1, 2, 3, 4, 5]

    # Последовательное выполнение и замер времени
    start_time = time.time()
    sequential_result = await get_multiple_users_sequential(user_ids)
    sequential_time = time.time() - start_time

    # Конкурентное выполнение и замер времени
    start_time = time.time()
    concurrent_result = await get_multiple_users_concurrent(user_ids)
    concurrent_time = time.time() - start_time

    # Вывод результатов
    print("Результаты последовательного выполнения:")
    for i, name in enumerate(sequential_result, 1):
        print(f"Пользователь {i}: {name}")
    print(f"Время выполнения (последовательное): {sequential_time:.4f} секунд\n")

    print("Результаты конкурентного выполнения:")
    for i, name in enumerate(concurrent_result, 1):
        print(f"Пользователь {i}: {name}")
    print(f"Время выполнения (конкурентное): {concurrent_time:.4f} секунд\n")

    print(f"Ускорение: в {sequential_time / concurrent_time:.2f} раз")


# Запуск программы
asyncio.run(main())
