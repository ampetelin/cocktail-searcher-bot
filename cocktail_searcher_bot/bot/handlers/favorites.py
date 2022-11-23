from aiogram import F
from aiogram.dispatcher.router import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.services.cocktail_searcher import exceptions as css_exceptions
from bot.services.cocktail_searcher.service import CocktailSearcherService, RecipeCallback, RemoveFavorite
from bot.states import FavoriteStates
from utils.aiogram.types import PaginationCallback

router = Router()
cocktail_searcher_service = CocktailSearcherService()


@router.callback_query(Text('favorites'))
async def favorites_button_handler(callback: CallbackQuery, state: FSMContext):
    page = 1
    try:
        telegram_user_id = await cocktail_searcher_service.get_telegram_user_id(callback.from_user.id)
        answer = await cocktail_searcher_service.get_favorite_cocktail_message(telegram_user_id, page)
    except (css_exceptions.TelegramUserNotFoundError, css_exceptions.CocktailNotFoundError):
        return await callback.answer('Список избранных коктейлей пуст', show_alert=True)

    message = await callback.message.edit_text(
        answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode
    )
    await state.update_data(telegram_user_id=telegram_user_id, page=page, paginated_message_id=message.message_id)
    await state.set_state(FavoriteStates.COCKTAIL_DISPLAY_STATE)


@router.callback_query(PaginationCallback.filter(), FavoriteStates.COCKTAIL_DISPLAY_STATE)
async def cocktail_pagination_handler(callback: CallbackQuery, callback_data: PaginationCallback, state: FSMContext):
    page = callback_data.page

    data = await state.get_data()
    telegram_user_id = data['telegram_user_id']
    await state.update_data(page=page)

    answer = await cocktail_searcher_service.get_favorite_cocktail_message(telegram_user_id, page)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()


@router.callback_query(RecipeCallback.filter(), FavoriteStates.COCKTAIL_DISPLAY_STATE)
async def recipe_button_handler(callback: CallbackQuery, callback_data: RecipeCallback, state: FSMContext):
    try:
        answer = await cocktail_searcher_service.get_cocktail_recipe_message(callback_data.cocktail_id)
    except css_exceptions.CocktailRecipeNotFoundError:
        return await callback.answer('У этого коктейля пока нет метода приготовления', show_alert=True)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()
    await state.set_state(FavoriteStates.RECIPE_COCKTAIL_DISPLAY_STATE)


@router.callback_query(F.data == 'back', FavoriteStates.RECIPE_COCKTAIL_DISPLAY_STATE)
async def back_to_cocktail_button_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    telegram_user_id = data['telegram_user_id']
    page = data['page']

    answer = await cocktail_searcher_service.get_favorite_cocktail_message(telegram_user_id, page)

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
    await callback.answer()
    await state.set_state(FavoriteStates.COCKTAIL_DISPLAY_STATE)


@router.callback_query(RemoveFavorite.filter(), FavoriteStates.COCKTAIL_DISPLAY_STATE)
async def remove_from_favorites_button_handler(callback: CallbackQuery,
                                               callback_data: RemoveFavorite,
                                               state: FSMContext):
    await cocktail_searcher_service.remove_cocktail_from_favorites(callback_data.favorite_id)

    data = await state.get_data()
    telegram_user_id = data['telegram_user_id']
    page = data['page']

    try:
        answer = await cocktail_searcher_service.get_favorite_cocktail_message(telegram_user_id, page - 1 or 1)
    except css_exceptions.CocktailNotFoundError:
        await state.update_data(paginated_message_id=None)
        return await callback.message.edit_text('Список избранного пуст.\n'
                                                'Нажмите /start для возвращения в главное меню.')

    await callback.message.edit_text(answer.text, reply_markup=answer.reply_markup, parse_mode=answer.parse_mode)
