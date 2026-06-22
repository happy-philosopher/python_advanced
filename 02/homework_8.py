# 8. Работа с asyncio.gather.
# Напишите функцию fetch_multiple_posts(post_ids), которая: принимает список ID постов,
# использует asyncio.gather для одновременного получения всех постов, возвращает список постов.
# URL: https://jsonplaceholder.typicode.com/posts/{post_id}


import aiohttp
import asyncio


async def fetch_post(post_id):
    """
    Асинхронно получает данные о посте по его ID.
    Возвращает словарь с данными поста или None в случае ошибки.
    """
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if 200 <= response.status < 300:
                    post_data = await response.json()
                    return post_data
                else:
                    print(f"HTTP-ошибка {response.status} при получении поста {post_id}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Сетевая ошибка при получении поста {post_id}: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при получении поста {post_id}: {e}")
        return None


async def fetch_multiple_posts(post_ids):
    """
    Получает данные о нескольких постах одновременно.
    Использует asyncio.gather для конкурентного выполнения запросов.
    Args:
        post_ids (list): список ID постов
    Returns:
        list: список словарей с данными постов (или None для неудачных запросов)
    """
    # Создаём список корутин для каждого поста
    tasks = [fetch_post(post_id) for post_id in post_ids]

    # Выполняем все запросы одновременно и ждём результатов
    posts = await asyncio.gather(*tasks, return_exceptions=True)

    return posts


async def main():
    # Тестовый список ID постов
    post_ids = [1, 2, 3, 4, 5, 6, 7]

    print(f"Получаем данные о постах с ID: {post_ids}")
    posts = await fetch_multiple_posts(post_ids)

    print("\n--- Результаты ---")
    for i, post in enumerate(posts):
        if post is not None:
            print(f"Пост {post['id']}: {post['title']}")
        else:
            print(f"Не удалось получить данные для поста с ID {post_ids[i]}")


# Запуск программы
asyncio.run(main())
