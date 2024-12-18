from app.database.models import async_session
from app.database.models import User, Task
from sqlalchemy import select


def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner


@connection
async def get_user(session, tg_id):
    async with async_session.begin():
        return await session.scalar(select(User).where(User.tg_id == tg_id))
    

@connection
async def set_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit() 


@connection
async def save_user(session, tg_id: int, name: str, phone: str):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.name = name
        user.phone = phone
    else:
        new_user = User(tg_id=tg_id, name=name, phone=phone)
        session.add(new_user)
    await session.commit()


@connection
async def save_task(session, title: str, description: str, user_id: int):
    user = await session.scalar(select(User).where(User.tg_id == user_id))
    if not user:
        raise ValueError(f"Пользователь с tg_id {user_id} не найден.")
    new_task = Task(user_id=user_id, description=description, is_completed=False, title=title)
    session.add(new_task)
    await session.commit()


@connection
async def get_tasks(session, user_id: int) -> list[Task]:
    tasks = await session.scalars(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    return tasks.all() 


@connection
async def get_task_by_id(session, task_id: int) -> Task | None:
    return await session.scalar(select(Task).where(Task.id == task_id))


@connection
async def delete_task(session, task_id: int):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        await session.delete(task)
        await session.commit()
    return task


@connection
async def mark_task_as_completed(session, task_id: int):
    task = await session.scalar(select(Task).where(Task.id == task_id))  
    if task:
        task.is_completed = True
        await session.commit()


@connection
async def delete_task(session, task_id: int):
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if task:
        await session.delete(task)
        await session.commit()


@connection
async def get_tasks_by_keywords(session, user_id: int, keyword: str):
    return await session.scalars(select(Task).where(
        Task.user_id == user_id,
        (Task.title.ilike(f"%{keyword}%")) | (Task.description.ilike(f"%{keyword}%"))
    ))
