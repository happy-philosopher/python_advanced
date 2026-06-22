# 7. И спользование create_task.
# Создайте программу, которая: запускает три задачи с помощью asyncio.create_task(),
# каждая задача выполняется разное время (1, 2, 3 секунды), выводит сообщение о завершении каждой задачи,
# а в конце выводит общее время выполнения.


import asyncio
import time


async def task_with_delay(task_id, delay):
    """
    Асинхронная задача, которая ждёт указанное количество секунд,
    а затем выводит сообщение о завершении.
    """
    print(f"Задача {task_id} запущена, задержка: {delay} сек.")
    await asyncio.sleep(delay)
    print(f"Задача {task_id} завершена")
    return f"Результат задачи {task_id}"


async def main():
    # Замеряем общее время выполнения
    start_time = time.time()

    # Создаём три задачи с разными задержками
    task1 = asyncio.create_task(task_with_delay(1, 3))
    task2 = asyncio.create_task(task_with_delay(2, 2))
    task3 = asyncio.create_task(task_with_delay(3, 1))

    # Ждём завершения всех задач
    results = await asyncio.gather(task1, task2, task3)

    # Вычисляем общее время выполнения
    end_time = time.time()
    total_time = end_time - start_time

    # Вывод результатов
    print("\n--- Результаты выполнения ---")
    for result in results:
        print(result)

    print(f"\nОбщее время выполнения: {total_time:.4f} секунд")


# Запуск программы
asyncio.run(main())
