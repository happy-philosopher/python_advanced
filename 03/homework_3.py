# Создайте эндпойнт /greet/{name}, который приветствует пользователя
# по имени. Добавьте необязательный query-параметр age для указания
# возраста.


from fastapi import FastAPI, Query
from typing import Optional


app = FastAPI()


@app.get("/greet/{name}")
def greet(name: str, age: Optional[int] = Query(None, ge=0, le=150)):
    if age is not None:
        return {"message": f"Привет, {name}! Тебе {age} лет."}
    return {"message": f"Привет, {name}!"}
