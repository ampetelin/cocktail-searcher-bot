from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.helplers import clear_previous_paginated_message_markup
from bot.services.cocktail_searcher import exceptions as cocktail_searcher_service_exceptions
from bot.services.cocktail_searcher.service import CocktailSearcherService, RecipeCallback, AddFavoriteCallback
from bot.states import SearchStates
from utils.aiogram.types import PaginationCallback

router = Router()
cocktail_searcher_service = CocktailSearcherService()


@router.callback_query(F.data == 'search')
async def search_button_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите название коктейля, категорию или содержащиеся в нем ингредиенты')
    await state.set_state(SearchStates.QUERY_INPUT_STATE)


@router.message(SearchStates.QUERY_INPUT_STATE)
@router.message(SearchStates.COCKTAIL_DISPLAY_STATE)
async def process_entered_search_query_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == SearchStates.COCKTAIL_DISPLAY_STATE:
        await clear_previous_paginated_message_markup(state)
        await state.set_state(SearchStates.QUERY_INPUT_STATE)

    search_query = message.text
    page = 1

    try:
        answer = await cocktail_searcher_service.get_cocktail_message(search_query, page)
    except cocktail_searcher_service_exceptions.CocktailNotFoundError:
        return await message.answer('К сожалению, мне не удалось найти такие коктейли. Попробуйте изменить ваш запрос')

    message = await message.answer(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await state.update_data(search_query=search_query, page=page, paginated_message_id=message.message_id)
    await state.set_state(SearchStates.COCKTAIL_DISPLAY_STATE)


@router.callback_query(PaginationCallback.filter(), SearchStates.COCKTAIL_DISPLAY_STATE)
async def cocktail_pagination_callback_handler(callback: CallbackQuery,
                                               callback_data: PaginationCallback,
                                               state: FSMContext):
    page = callback_data.page

    data = await state.get_data()
    search_query = data['search_query']
    await state.update_data(page=page)

    answer = await cocktail_searcher_service.get_cocktail_message(search=search_query, page=page)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()


@router.callback_query(RecipeCallback.filter(), SearchStates.COCKTAIL_DISPLAY_STATE)
async def recipe_button_handler(callback: CallbackQuery, callback_data: RecipeCallback, state: FSMContext):
    try:
        answer = await cocktail_searcher_service.get_cocktail_recipe_message(callback_data.cocktail_id)
    except cocktail_searcher_service_exceptions.CocktailRecipeNotFoundError:
        return await callback.answer('У этого коктейля пока нет метода приготовления', show_alert=True)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()
    await state.set_state(SearchStates.RECIPE_DISPLAY_STATE)


@router.callback_query(F.data == 'back', SearchStates.RECIPE_DISPLAY_STATE)
async def back_to_cocktail_button_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    search_query = data['search_query']
    page = data['page']

    answer = await cocktail_searcher_service.get_cocktail_message(search_query, page)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()
    await state.set_state(SearchStates.COCKTAIL_DISPLAY_STATE)


@router.callback_query(AddFavoriteCallback.filter(), SearchStates.COCKTAIL_DISPLAY_STATE)
async def add_to_favorites_button_handler(callback: CallbackQuery,
                                          callback_data: AddFavoriteCallback,
                                          state: FSMContext):
    data = await state.get_data()
    telegram_user_id = data.get('telegram_user_id')

    if not telegram_user_id:
        telegram_user_chat_id = callback.from_user.id
        try:
            telegram_user_id = await cocktail_searcher_service.get_telegram_user_id(telegram_user_chat_id)
        except cocktail_searcher_service_exceptions.TelegramUserNotFoundError:
            telegram_user_id = await cocktail_searcher_service.create_telegram_user(telegram_user_chat_id)
        await state.update_data(telegram_user_id=telegram_user_id)

    try:
        await cocktail_searcher_service.add_cocktail_to_favorites(telegram_user_id, callback_data.cocktail_id)
    except cocktail_searcher_service_exceptions.CocktailAlreadyInFavoritesError:
        return await callback.answer('Коктейль уже добавлен в избранное', show_alert=True)

    await callback.answer('Коктейль добавлен в избранное', show_alert=True)
