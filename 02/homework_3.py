# 3. Работа с event loop.
# Создайте корутину download_file(file_name, delay), которая: имитирует скачивание файла с задержкой delay секунд -
# выводит "Начинаем скачивание {file_name}", ждет указанное время, выводит "Файл {file_name} скачан".
# Запустите три таких корутины с разными задержками (1, 2, 3 секунды).


import asyncio


async def download_file(file_name, delay):
    print(f"Начинаем скачивание {file_name}")
    await asyncio.sleep(delay)
    print(f"Файл {file_name} скачан")


async def main():
    # Создаём три корутины с разными задержками
    task1 = asyncio.create_task(download_file("file1.txt", 2))
    task2 = asyncio.create_task(download_file("file2.txt", 3))
    task3 = asyncio.create_task(download_file("file3.txt", 1))

    # Ждём завершения всех корутин
    await task1
    await task2
    await task3


# Запускаем событийный цикл
asyncio.run(main())
