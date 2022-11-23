from aiogram.fsm.context import FSMContext


async def clear_previous_paginated_message_markup(state: FSMContext):
    """Очищает разметку клавиатуры пагинации у предыдущего сообщения"""
    data = await state.get_data()

    paginated_message_id = data.get('paginated_message_id')
    if not paginated_message_id:
        return

    await state.bot.edit_message_reply_markup(state.key.chat_id, paginated_message_id, reply_markup=None)
    await state.update_data(paginated_message_id=None)
