# 4. Асинхронный запрос к API.
# Используя библиотеку aiohttp, напишите функцию fetch_user(user_id):
# делает GET-запрос к https://jsonplaceholder.typicode.com/users/{user_id}, возвращает имя пользователя.
# Запустите функцию для user_id = 1.


import aiohttp
import asyncio


async def fetch_user(user_id):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                user_data = await response.json()
                return user_data.get('name')
            else:
                raise Exception(f"Ошибка при запросе: статус {response.status}")


async def main():
    try:
        user_name = await fetch_user(1)
        print(f"Имя пользователя с ID = 1: {user_name}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Запускаем асинхронную функцию
asyncio.run(main())
