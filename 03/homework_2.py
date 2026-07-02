# Добавьте эндпойнт /calculate/add/{a}/{b}, который складывает два
# числа и возвращает результат.


from fastapi import FastAPI, Path
from pydantic import BaseModel, Field


app = FastAPI()


# Модель ответа для фильма
class MovieInfoResponse(BaseModel):
    title: str = Field(min_length=1, description="Название фильма")
    director: str = Field(min_length=1, description="Режиссёр")
    year: int = Field(ge=1888, le=2099, description="Год выпуска")


@app.get("/info", response_model=MovieInfoResponse)
def get_movie_info() -> MovieInfoResponse:
    movie_data = {
        "title": "Интерстеллар",
        "director": "Кристофер Нолан",
        "year": 2014,
    }
    return MovieInfoResponse(**movie_data)


# Модель ответа для сложения
class AddResponse(BaseModel):
    a: int
    b: int
    result: int


@app.get("/calculate/add/{a}/{b}", response_model=AddResponse)
def calculate_add(a: int = Path(ge=-10_000_000, le=10_000_000),
                  b: int = Path(ge=-10_000_000, le=10_000_000)) -> AddResponse:
    """
    Складывает два целых числа a и b.
    Диапазон допустимых значений: [-10_000_000; 10_000_000].
    """
    return AddResponse(a=a, b=b, result=a + b)
