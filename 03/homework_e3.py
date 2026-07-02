# Разработка API для интернет-магазина:
# 1. Две таблицы: Products (товары) и Orders (заказы).
# 2. Products: название, описание, цена, количество на складе.
# 3. Orders: номер заказа, список товаров (JSON), общая стоимость, статус.
# 4. Эндпоинт создания заказа должен:
#   - проверить наличие товаров на складе;
#   - вернуть ошибку 400, если товаров недостаточно;
#   - уменьшить количество товаров на складе;
#   - отправить в фоне "уведомление" (запись в лог).
# 5. Асинхронные эндпоинты для получения списков.
# 6. Pydantic модели с валидацией (цена > 0, количество ≥ 0).
# 7. Зависимости для БД и проверки прав доступа (например, только "администратор" может изменять товары).


from __future__ import annotations
from typing import List
from datetime import datetime, timezone
from enum import StrEnum
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import logging


# --- Конфигурация БД (SQLite для простоты) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Модели БД ---
class OrderStatus(StrEnum):
    PENDING = "pending"        # В обработке
    PAID = "paid"              # Оплачен
    SHIPPED = "shipped"        # Отправлен
    CANCELLED = "cancelled"    # Отменён


class Product(Base):
    __tablename__ = "products"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)
    price: float = Column(Float, nullable=False)
    quantity: int = Column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True, index=True)
    order_number: str = Column(String, unique=True, nullable=False)
    # В БД храним как JSON-список словарей — это ок
    items: dict = Column(JSON, nullable=False)
    total_cost: float = Column(Float, nullable=False)
    status: OrderStatus = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: datetime = Column(DateTime, default=datetime.now(timezone.utc))


# Создаём таблицы
Base.metadata.create_all(bind=engine)


# --- Pydantic модели ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название товара")
    description: str = Field(..., min_length=1, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена должна быть больше 0")
    quantity: int = Field(..., ge=0, description="Количество на складе должно быть неотрицательным")


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0, description="ID товара должен быть положительным")
    qty: int = Field(..., gt=0, description="Количество товара в заказе должно быть положительным")


class OrderCreate(BaseModel):
    items: List[OrderItem] = Field(..., min_length=1, description="Список позиций заказа не может быть пустым")


class OrderResponse(BaseModel):
    id: int
    order_number: str
    items: List[OrderItem]
    total_cost: float
    status: OrderStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Зависимости ---
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_role(role: str | None = None) -> str:
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует параметр role для проверки прав доступа"
        )
    return role


def require_admin(role: str = Depends(get_current_user_role)) -> None:
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут выполнять это действие"
        )


# --- Фоновая задача: логирование уведомлений ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("shop_notifications")


def log_notification(message: str) -> None:
    logger.info(f"[УВЕДОМЛЕНИЕ] {message}")


# --- Эндпоинты ---
app = FastAPI(title="API интернет‑магазина", description="Управление товарами и заказами")


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
) -> ProductResponse:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    log_notification(f"Создан новый товар: {db_product.name} (ID: {db_product.id})")
    return db_product


@app.get("/products", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)) -> List[ProductResponse]:
    products = db.query(Product).all()
    return products


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductBase,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
) -> ProductResponse:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    log_notification(f"Обновлён товар: {db_product.name} (ID: {product_id})")
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin)
) -> None:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    db.delete(db_product)
    db.commit()
    log_notification(f"Удалён товар с ID: {product_id}")


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
) -> OrderResponse:
    total_cost = 0.0
    items_to_update: list[tuple[Product, int]] = []

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар с ID {item.product_id} не найден"
            )
        if product.quantity < item.qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Недостаточно товара на складе: запрашивается {item.qty} шт., "
                    f"доступно {product.quantity} шт. (товар ID: {item.product_id})"
                )
            )
        total_cost += product.price * item.qty
        items_to_update.append((product, item.qty))

    # Уменьшаем количество товаров на складе
    for product, qty in items_to_update:
        product.quantity -= qty

    order_number = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{id(order)}"
    db_order = Order(
        order_number=order_number,
        items=[{"product_id": i.product_id, "qty": i.qty} for i in order.items],
        total_cost=total_cost,
        status=OrderStatus.PENDING
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    log_notification(
        f"Создан заказ №{order_number}, статус: {db_order.status.value}, "
        f"общая стоимость: {total_cost:.2f} руб."
    )

    return db_order


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderResponse:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


@app.get("/orders", response_model=List[OrderResponse])
async def list_orders(db: Session = Depends(get_db)) -> List[OrderResponse]:
    orders = db.query(Order).all()
    return orders


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
