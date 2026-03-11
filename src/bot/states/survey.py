from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    choosing_category = State()
    answering_step = State()
    multi_select_step = State()
    text_input_step = State()


class ChatStates(StatesGroup):
    chatting = State()


class OrderStates(StatesGroup):
    confirming = State()
