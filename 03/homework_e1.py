# Создание мини-блога API с SQLite:
# - Эндпоинты для создания, чтения, обновления и удаления постов.
# - Каждый пост имеет: заголовок, содержание, автора, дату создания.
# - Реализуйте поиск постов по ключевым словам в заголовке.
# - Добавьте пагинацию для списка постов.
# - Используйте Pydantic модели для валидации.
# - Обработайте ошибки 404 при попытке получить несуществующий пост.


from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session


# --- DB setup ---
DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


# --- Pydantic models (Pydantic v2 style) ---
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    author: Optional[str] = Field(None, min_length=1, max_length=100)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginatedPosts(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    page_size: int


# --- App ---
app = FastAPI(title="Mini Blog API")

# Зависимость для сессии БД (правильно для FastAPI)
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = PostDB(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post  # благодаря from_attributes это корректно маппится в PostResponse


@app.get("/posts", response_model=PaginatedPosts)
def list_posts(
    q: Optional[str] = Query(None, description="Поиск по ключевым словам в заголовке"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(PostDB)

    if q:
        query = query.filter(PostDB.title.ilike(f"%{q}%"))

    total = query.count()
    offset = (page - 1) * page_size
    posts = query.order_by(PostDB.created_at.desc()).offset(offset).limit(page_size).all()

    return PaginatedPosts(
        items=posts,
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return post


@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    data = post_update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    db.delete(post)
    db.commit()
