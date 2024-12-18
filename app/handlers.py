# Команда /start
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.database.request import (set_user, 
                                  save_user, 
                                  save_task, 
                                  get_tasks, 
                                  get_task_by_id, 
                                  mark_task_as_completed, 
                                  delete_task,
                                  get_user,
                                  get_tasks_by_keywords)
import app.keyboards as kb
from app.state import RegisterStates, TaskStates
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    if user:
        await message.answer("👋 *Добро пожаловать обратно!* Вы уже зарегистрированы. "
            "Используйте кнопки ниже для управления вашими задачами.",
            reply_markup=kb.task,
            parse_mode="Markdown")
    else:
        await set_user(message.from_user.id)
        await message.answer("👋 *Приветствуем в Task Manager!* 🚀\n\n"
            "Нажмите *Регистрация 📋*, чтобы создать аккаунт и начать пользоваться.",
            reply_markup=kb.register_kb,
            parse_mode="Markdown")


@router.message(F.text == 'Регистрация 📋')
async def register_user(message: Message, state: FSMContext):
    await message.answer("📋 *Регистрация пользователя*\n\nВведите ваше имя для начала:",
        parse_mode="Markdown")
    await state.set_state(RegisterStates.name)


@router.message(RegisterStates.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Теперь введите ваш номер телефона (например, +123456789):",
        parse_mode="Markdown")
    await state.set_state(RegisterStates.phone)


@router.message(RegisterStates.phone)
async def process_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    name = data['name']
    phone = message.text
    await save_user(tg_id=user_id, name=name, phone=phone)
    await state.clear()
    await message.answer("🎉 *Регистрация завершена!* Теперь вы можете добавлять задачи и управлять ими.",
        reply_markup=kb.task,
        parse_mode="Markdown")


@router.message(F.text == '➕Добавить задачу')
async def add_task(message: Message, state: FSMContext):
    await message.answer("✏️ Введите название задачи, чтобы начать:")
    await state.set_state(TaskStates.title)


@router.message(TaskStates.title)
async def process_title(message: Message, state: FSMContext):
    task_title = message.text
    await state.update_data(title=task_title)
    await message.answer( "📖 Теперь введите описание задачи:")
    await state.set_state(TaskStates.description)


@router.message(TaskStates.description)
async def process_description(message: Message, state: FSMContext):
    task_description = message.text
    data = await state.get_data()
    task_title = data['title'] 
    await save_task(title=task_title, description=task_description, user_id=message.from_user.id)
    await state.clear()
    await message.answer("✅ *Задача успешно добавлена!* Используйте меню для управления задачами.",parse_mode="Markdown")


@router.message(F.text == "📋Список задач")
async def tasks_list(message: Message):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id=user_id)
    if not tasks:
        await message.answer( "⚠️ *У вас пока нет задач.*\n\nДобавьте новую, чтобы начать.",parse_mode="Markdown")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for task in tasks:
        task_text = f"✅ {task.title}" if task.is_completed else task.title
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=task_text,
                callback_data=f"task_{task.id}"
            )
        ])

    await message.answer( "📝 *Ваши задачи:*\n\nВыберите задачу для подробностей.",reply_markup=keyboard,parse_mode="Markdown")


@router.callback_query(F.data.startswith("task_"))
async def task_detail(callback_query: CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[1])
    task = await get_task_by_id(task_id=task_id)
    if not task:
        await callback_query.message.answer(  "⚠️ *Задача не найдена.* Возможно, она была удалена.",parse_mode="Markdown")
        return
    await state.set_state(TaskStates.task_id)
    await state.update_data(task_id=task_id)
    message_text = f"📌 *{task.title}*\n"f"📖 {task.description}\n\n"f"Статус: {'✅ Выполнена' if task.is_completed else '🔘 В процессе'}"
    await callback_query.message.answer(message_text, reply_markup=kb.completed_delete, parse_mode='Markdown')
    await callback_query.answer()



@router.message(F.text == "✅Выполнить")
async def task_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    if task_id:
        await mark_task_as_completed(task_id=task_id)
        await message.answer("✅ *Задача успешно выполнена!*",reply_markup=kb.task,parse_mode="Markdown")
        await state.clear()

@router.message(F.text == "🗑Удалить")
async def task_delete(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    if task_id:
        await delete_task(task_id=task_id)
        await message.answer("🗑 *Задача успешно удалена!*",reply_markup=kb.task,parse_mode="Markdown")
        await state.clear()

@router.message(F.text=="🔍Найти задачу")
async def start_search(message: Message, state: FSMContext):
    await state.set_state(TaskStates.search)
    await message.answer( "🔍 Введите ключевое слово для поиска задачи (например, часть названия или описания):",parse_mode="Markdown")


@router.message(TaskStates.search)
async def search_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    search_text = message.text.strip().lower()
    tasks = await get_tasks_by_keywords(user_id=user_id, keyword=search_text)
    if tasks:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for task in tasks:
            task_text = f"✅ {task.title}" if task.is_completed else task.title
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text=task_text, callback_data=f"task_{task.id}")
            ])
        await message.answer(f"🔍 *Результаты поиска по запросу:* `{search_text}`",reply_markup=keyboard,parse_mode="Markdown")
    else:
        await message.answer(f"⚠️ *Задачи, соответствующие запросу* `{search_text}`, *не найдены.*",parse_mode="Markdown")

    await state.clear()

