# Создайте API с эндпойнтом /info, который возвращает информацию о
# вашем любимом фильме (название, режиссер, год выпуска).


from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI()


class MovieInfoResponse(BaseModel):
    title: str = Field(min_length=1, description="Название фильма")
    director: str = Field(min_length=1, description="Режиссёр")
    year: int = Field(ge=1888, le=2099, description="Год выпуска (в диапазоне 1888–2099)")


@app.get("/info", response_model=MovieInfoResponse)
def get_movie_info() -> MovieInfoResponse:
    """
    Возвращает информацию о любимом фильме.
    """
    movie_data = {
        "title": "Интерстеллар",
        "director": "Кристофер Нолан",
        "year": 2014,
    }

    return MovieInfoResponse(**movie_data)


# Для запуска перейти в директорию 03/: uvicorn homework_1:app --reload
