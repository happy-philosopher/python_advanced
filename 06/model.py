import datetime
import enum
from datetime import timezone
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.sqlite import JSON


# ---------- Модель и БД ----------
Base = declarative_base()


class TaskStatus(enum.Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)          # хранит произвольные данные
    status = Column(String(20), default=TaskStatus.pending.value)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Индекс для быстрого поиска задачи с наивысшим приоритетом
    __table_args__ = (
        Index('idx_status_priority_created', 'status', 'priority', 'created_at'),
    )


# ---------- Функция атомарного захвата задачи ----------
def fetch_highest_priority_task(session):
    """
    Атомарно забирает задачу с наивысшим приоритетом (статус 'pending').
    Возвращает объект Task или None.
    """
    # Подзапрос: ID задачи с макс. приоритетом (и ранней датой создания при равных приоритетах)
    subq = (
        session.query(Task.id)
        .filter(Task.status == TaskStatus.pending.value)
        .order_by(Task.priority.desc(), Task.created_at.asc())
        .limit(1)
        .scalar_subquery()
    )

    # Обновляем статус и время старта, только если задача всё ещё 'pending'
    rows_updated = session.query(Task).filter(
        Task.id == subq,
        Task.status == TaskStatus.pending.value
    ).update(
        {
            Task.status: TaskStatus.processing.value,
            Task.started_at: datetime.datetime.now(timezone.utc)
        },
        synchronize_session=False
    )
    session.commit()

    # Если обновление затронуло строку – загружаем задачу и возвращаем
    if rows_updated:
        return session.query(Task).filter(Task.id == subq).first()
    return None


# ---------- Функция добавления тестовых задач ----------
def add_sample_tasks(session):
    """Добавляет 5 задач с разными приоритетами, если таблица пуста."""
    # Проверяем, есть ли уже задачи
    count = session.query(Task).count()
    if count > 0:
        print(f"В БД уже есть {count} задач. Пропускаем добавление.")
        return

    tasks = [
        Task(task_type='email', payload={'to': 'alice@example.com', 'subject': 'Welcome'}, priority=2),
        Task(task_type='report', payload={'date': '2025-01-01', 'format': 'pdf'}, priority=5),
        Task(task_type='backup', payload={'path': '/data', 'compressed': True}, priority=3),
        Task(task_type='email', payload={'to': 'bob@example.com', 'subject': 'Invoice'}, priority=2),
        Task(task_type='cleanup', payload={'older_than_days': 30}, priority=1),
    ]
    session.add_all(tasks)
    session.commit()
    print(f"✅ Добавлено {len(tasks)} тестовых задач.")


# ---------- Основной блок ----------
if __name__ == "__main__":
    # Подключаемся к SQLite (используем IMMEDIATE для конкурентной работы)
    engine = create_engine('sqlite:///tasks.db?isolation_level=IMMEDIATE', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Добавляем задачи (только если таблица пуста)
    add_sample_tasks(session)

    # Захватываем самую приоритетную задачу
    task = fetch_highest_priority_task(session)
    if task:
        print(f"🚀 Задача {task.id} взята в обработку:")
        print(f"   Тип: {task.task_type}")
        print(f"   Приоритет: {task.priority}")
        print(f"   Данные: {task.payload}")
        print(f"   Начало обработки: {task.started_at}")
    else:
        print("ℹ️ Нет задач для обработки.")
