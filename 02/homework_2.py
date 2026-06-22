# 2. Сравнение времени выполнения.
# Создайте две версии программы, синхронную: три последовательных вызова time.sleep(1),
# асинхронную: три конкурентных вызова await asyncio.sleep(1).
# Измерьте и сравните время выполнения обеих версий.


import time
import asyncio


# Синхронная часть - три последовательных вызова
print("\nСинхронное выполнение:")
start_sync = time.perf_counter()
for i in range(3):
    print(f"Шаг {i+1}: начало")
    time.sleep(1)
    print(f"Шаг {i+1}: конец")
end_sync = time.perf_counter()
print(f"Общее время (синхронно): {end_sync - start_sync:.2f} сек\n")


# Асинхронная часть - три конкурентных вызова
async def async_task(i):
    print(f"Задача {i+1}: начало")
    await asyncio.sleep(1)
    print(f"Задача {i+1}: конец")


async def main():
    print("Асинхронное выполнение:")
    start_async = time.perf_counter()
    await asyncio.gather(*[async_task(i) for i in range(3)])
    end_async = time.perf_counter()
    print(f"Общее время (асинхронно): {end_async - start_async:.3f} сек")


asyncio.run(main())
