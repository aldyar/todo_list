from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

register_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Регистрация 📋')]], resize_keyboard=True)
task = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='➕Добавить задачу'),
                                         KeyboardButton(text='📋Список задач')],
                                         [KeyboardButton(text='🔍Найти задачу')]], resize_keyboard=True)

completed_delete = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = "✅Выполнить"),
    KeyboardButton(text = "🗑Удалить")]], resize_keyboard=True)