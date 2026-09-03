import csv
from typing import Dict


def aggregate_sales(csv_file_path: str) -> Dict[str, float]:
    """
    Читает CSV с колонками: дата, товар, количество, сумма
    Возвращает словарь: {'total_sum': float, 'sales_count': int, 'average_check': float}
    """
    total_sum = 0.0
    sales_count = 0

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # ожидаем заголовки: дата, товар, количество, сумма
        for row in reader:
            # Преобразуем сумму (может быть с запятой, но обычно точка)
            amount = float(row['сумма'].replace(',', '.'))
            total_sum += amount
            sales_count += 1

    average_check = total_sum / sales_count if sales_count else 0.0
    return {
        'total_sum': total_sum,
        'sales_count': sales_count,
        'average_check': average_check
    }


result = aggregate_sales('sales.csv')
print(result)
