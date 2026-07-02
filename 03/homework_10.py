# Создайте эндпойнт /divide/{a}/{b}, который возвращает ошибку 400 при попытке деления на ноль,
# либо результат деления при корректных значениях.


from fastapi import FastAPI, HTTPException, status


app = FastAPI()


@app.get("/divide/{a}/{b}")
def divide(a: float, b: float):
    if b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Деление на ноль не допускается."
        )
    return {"result": a / b}
