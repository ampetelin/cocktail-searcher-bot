from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.helplers import clear_previous_paginated_message_markup

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    message_text = "Привет! Я бот Cocktail Searcher 🤖\n\n" \
                   "Моя задача - помочь вам найти любимый коктейль 🍹"
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Поиск', callback_data='search')],
                         [InlineKeyboardButton(text='Избранное', callback_data='favorites')]]
    )
    await clear_previous_paginated_message_markup(state)
    await state.clear()
    await message.answer(message_text, reply_markup=reply_markup)
