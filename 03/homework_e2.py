# Создание API системы управления задачами:
# - Таблица SQLite с задачами (название, описание, приоритет, статус, дата создания).
# - CRUD операции для задач.
# - Эндпоинт для фильтрации задач по статусу и приоритету.
# - Используйте зависимости для подключения к БД.
# - Реализуйте фоновую задачу, которая логирует каждое изменение задачи в файл.
# - Правильные HTTP статус-коды для всех операций.


import sqlite3
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict


DATABASE_URL = "tasks.db"
LOG_FILE = "task_log.txt"

# Настройка логгера
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("task_logger")


def log_task_change(action: str, task_id: int, old_data: Optional[Dict[str, Any]], new_data: Dict[str, Any]):
    msg = f"Action: {action}, Task ID: {task_id}"
    if old_data is not None:
        msg += f" | Before: {old_data}"
    msg += f" | After: {new_data}"
    logger.info(msg)


# Pydantic модели
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=4000)
    priority: int = Field(default=1, ge=1, le=5)
    status: str = Field(default="pending", pattern=r"^(pending|in_progress|completed)$")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=4000)
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, pattern=r"^(pending|in_progress|completed)$")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    priority: int
    status: str
    created_at: datetime


# Инициализация БД
def init_db():
    with sqlite3.connect(DATABASE_URL) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


init_db()

app = FastAPI(title="API система управления задачами")


# Вспомогательная функция: просто открывает соединение
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks = None
):
    db = get_db_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        cur = db.cursor()

        cur.execute(
            """
            INSERT INTO tasks (title, description, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task.title, task.description, task.priority, task.status, now)
        )
        db.commit()
        new_id = cur.lastrowid

        new_data = {
            "id": new_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "created_at": now
        }

        if background_tasks is not None:
            background_tasks.add_task(log_task_change, "CREATE", new_id, None, new_data)

        cur.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        row = cur.fetchone()
        return TaskResponse(**dict(row))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()


@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[int] = None
):
    db = get_db_connection()
    try:
        query = "SELECT * FROM tasks"
        params = []
        conditions = []

        if status is not None:
            conditions.append("status = ?")
            params.append(status)
        if priority is not None:
            conditions.append("priority = ?")
            params.append(priority)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cur = db.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [TaskResponse(**dict(r)) for r in rows]
    finally:
        db.close()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    db = get_db_connection()
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse(**dict(row))
    finally:
        db.close()


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    background_tasks: BackgroundTasks = None
):
    db = get_db_connection()
    try:
        cur = db.cursor()

        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        old_row = cur.fetchone()
        if old_row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        old_data = dict(old_row)

        updates = []
        values = []

        if task.title is not None:
            updates.append("title = ?")
            values.append(task.title)
        if task.description is not None:
            updates.append("description = ?")
            values.append(task.description)
        if task.priority is not None:
            updates.append("priority = ?")
            values.append(task.priority)
        if task.status is not None:
            updates.append("status = ?")
            values.append(task.status)

        if not updates:
            return TaskResponse(**old_data)

        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cur.execute(query, values)
        db.commit()

        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        new_row = cur.fetchone()
        new_data = dict(new_row)

        if background_tasks is not None:
            background_tasks.add_task(log_task_change, "UPDATE", task_id, old_data, new_data)

        return TaskResponse(**new_data)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks = None
):
    db = get_db_connection()
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        old_data = dict(row)

        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()

        if background_tasks is not None:
            background_tasks.add_task(log_task_change, "DELETE", task_id, old_data, None)

        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        db.close()
