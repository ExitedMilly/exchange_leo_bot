from aiogram.fsm.state import State, StatesGroup


class ExchangeState(StatesGroup):
    WAITING_AMOUNT = State()
    CONFIRMATION = State()
