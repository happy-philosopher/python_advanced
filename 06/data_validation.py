import re
from datetime import datetime


def validate_record(record: dict) -> dict:
    """
    Проверяет поля 'email', 'phone', 'date' в переданном словаре.
    Возвращает словарь с полями и статусами валидации.
    """
    errors = {}

    # Проверка email
    email = record.get('email', '')
    if '@' not in email:
        errors['email'] = 'Отсутствует символ @'

    # Проверка телефона: только цифры, длина 10 или 11
    phone = record.get('phone', '')
    phone_digits = re.sub(r'\D', '', phone)  # удаляем всё кроме цифр
    if not (len(phone_digits) == 10 or len(phone_digits) == 11):
        errors['phone'] = 'Телефон должен содержать 10 или 11 цифр'
    elif phone_digits != phone:  # если были нецифровые символы
        errors['phone'] = 'Телефон должен состоять только из цифр'

    # Проверка даты в формате DD.MM.YYYY
    date_str = record.get('date', '')
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        errors['date'] = 'Дата должна быть в формате DD.MM.YYYY'

    # Результат: исходные данные + статус
    return {
        'record': record,
        'valid': len(errors) == 0,
        'errors': errors
    }


test = {'email': 'user@domain', 'phone': '89123456789', 'date': '15.08.2025'}
print(validate_record(test))
