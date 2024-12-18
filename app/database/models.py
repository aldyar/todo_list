from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from sqlalchemy import Integer, Text, ForeignKey, TIMESTAMP

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3',
                             echo=True)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async_session = async_sessionmaker(engine)


# Модель таблицы users
class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

# Модель таблицы tasks
class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.tg_id'), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)  # Название задачи
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание задачи
    is_completed: Mapped[bool] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)