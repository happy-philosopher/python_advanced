# 1. Создание первой корутины.
# Напишите асинхронную функцию greet(name), которая: принимает имя в качестве параметра выводит "Привет, {name}!"
# ждет 1 секунду (используя await asyncio.sleep(1)) выводит "До свидания, {name}!".
# Запустите эту функцию с помощью asyncio.run().


import asyncio


async def greet(name):
    print(f"Привет, {name}!")
    await asyncio.sleep(1)
    print(f"До свидания, {name}!")


asyncio.run(greet("Анна"))
