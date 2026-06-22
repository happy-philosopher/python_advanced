# A1. А синхронный парсер постов.
# Создайте программу, которая: получает список всех постов пользователя
# (https://jsonplaceholder.typicode.com/posts?userId={user_id}), для каждого поста получает его комментарии
# (https://jsonplaceholder.typicode.com/posts/{post_id}/comments), выводит статистику:
# количество постов и средний размер комментариев для пользователя.
# Все запросы должны выполняться асинхронно, реализуйте для userId = 1.


import aiohttp
import asyncio


async def fetch_user_posts(user_id):
    """Получает все посты пользователя по его ID."""
    url = f"https://jsonplaceholder.typicode.com/posts?userId={user_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    posts = await response.json()
                    return posts
                else:
                    print(f"HTTP-ошибка {response.status} при получении постов пользователя {user_id}")
                    return []
    except aiohttp.ClientError as e:
        print(f"Сетевая ошибка при получении постов пользователя {user_id}: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка при получении постов пользователя {user_id}: {e}")
        return []


async def fetch_post_comments(post_id):
    """Получает комментарии для конкретного поста."""
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}/comments"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    comments = await response.json()
                    return comments
                else:
                    print(f"HTTP-ошибка {response.status} при получении комментариев поста {post_id}")
                    return []
    except aiohttp.ClientError as e:
        print(f"Сетевая ошибка при получении комментариев поста {post_id}: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка при получении комментариев поста {post_id}: {e}")
        return []


async def analyze_user_posts_and_comments(user_id):
    """
    Анализирует посты и комментарии пользователя, выводит статистику.
    Args:
        user_id (int): ID пользователя для анализа
    """
    print(f"Анализируем данные пользователя с ID = {user_id}...")

    # Получаем все посты пользователя
    posts = await fetch_user_posts(user_id)
    post_count = len(posts)

    if post_count == 0:
        print("Не удалось получить посты пользователя или у пользователя нет постов.")
        return

    print(f"Найдено постов: {post_count}")

    # Создаём задачи для получения комментариев для каждого поста
    comment_tasks = [fetch_post_comments(post['id']) for post in posts]
    comments_lists = await asyncio.gather(*comment_tasks, return_exceptions=True)

    # Обрабатываем возможные исключения в результатах
    valid_comments_lists = []
    for comments in comments_lists:
        if isinstance(comments, Exception):
            print(f"Ошибка при получении комментариев: {comments}")
            valid_comments_lists.append([])
        else:
            valid_comments_lists.append(comments)

    # Считаем общее количество комментариев и суммарную длину текста комментариев
    total_comments = 0
    total_comment_length = 0

    for comments in valid_comments_lists:
        total_comments += len(comments)
        for comment in comments:
            total_comment_length += len(comment.get('body', ''))

    # Вычисляем средний размер комментария
    if total_comments > 0:
        average_comment_size = total_comment_length / total_comments
    else:
        average_comment_size = 0

    # Вывод статистики
    print("\n--- Статистика ---")
    print(f"Количество постов: {post_count}")
    print(f"Общее количество комментариев: {total_comments}")
    print(f"Средний размер комментария: {average_comment_size:.2f} символов")


async def main():
    user_id = 10
    await analyze_user_posts_and_comments(user_id)


# Запуск программы
asyncio.run(main())
