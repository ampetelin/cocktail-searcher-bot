import re

from aiogram.dispatcher.router import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent

from bot.services.cocktail_searcher import exceptions as css_exceptions

router = Router()


@router.errors(ExceptionTypeFilter(TelegramBadRequest))
async def message_not_modified_exception_handler(event: ErrorEvent):
    re_message_is_not_modified_error = re.compile('message is not modified')
    if re.search(re_message_is_not_modified_error, str(event.exception)):
        if event.update.callback_query:
            return await event.update.callback_query.answer()
    raise


@router.errors(ExceptionTypeFilter(css_exceptions.CocktailSearcherServiceError))
async def cocktail_searcher_service_exception_handler(event: ErrorEvent):
    await event.update.callback_query.answer('Упс... Что-то пошло не так... Попробуйте позже')
