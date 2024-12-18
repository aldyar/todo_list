from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    name = State()
    phone = State()

class TaskStates(StatesGroup):
    title = State()
    description = State()
    task_id = State()
    search = State()