from typing import Optional, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from jinja2 import Environment, select_autoescape, PackageLoader

from bot.clients.cocktail_searcher import exceptions as cs_exception
from bot.clients.cocktail_searcher.client import CocktailSearcherClient
from bot.clients.cocktail_searcher.models import Cocktail, CookingStage
from bot.services.cocktail_searcher import exceptions
from bot.services.cocktail_searcher.dtos import TelegramMessage, ParseMode
from utils.aiogram.types import InlinePaginationKeyboardMarkup

jinja2 = Environment(loader=PackageLoader(__name__, 'templates'), autoescape=select_autoescape())

COCKTAIL_PAGE_SIZE = 1


class RecipeCallback(CallbackData, prefix='recipe'):
    cocktail_id: int


class AddFavoriteCallback(CallbackData, prefix='add_favorite'):
    cocktail_id: int


class RemoveFavorite(CallbackData, prefix='remove_favorite'):
    favorite_id: int


class CocktailSearcherService:
    def __init__(self):
        self.api_client = CocktailSearcherClient()

    async def get_cocktail_message(self,
                                   search: Optional[str] = None,
                                   page: int = 1) -> TelegramMessage:
        """
        Получает сообщение, содержащее коктейль

        Args:
            search: строка запроса поиска коктейлей
            page: номер страницы

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            CocktailNotFoundError: возбуждаемое исключение в случае отсутствия коктейля
        """
        try:
            response = await self.api_client.get_cocktails(search, page, COCKTAIL_PAGE_SIZE)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)

        if not response.results:
            raise exceptions.CocktailNotFoundError("The external API returned an empty cocktail list")

        cocktail = response.results[0]
        text = self._build_cocktail_message_text(cocktail)
        reply_markup = self._build_cocktail_reply_markup(cocktail.id, page, response.total_pages)

        return TelegramMessage(text, reply_markup, ParseMode.HTML)

    async def get_favorite_cocktail_message(self,
                                            telegram_user_id: int,
                                            page: int = 1) -> TelegramMessage:
        """
        Получает сообщение, содержащее избранный коктейль

        Args:
            telegram_user_id: идентификатор пользователя Telegram
            page: номер страницы

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            TelegramUserNotFoundError: возбуждаемое исключение в случае отсутствия пользователя Telegram с указанным
                telegram_user_id
            CocktailNotFoundError: возбуждаемое исключение в случае отсутствия избранного коктейля у пользователя
                Telegram
        """
        try:
            response = await self.api_client.get_favorite_cocktails(telegram_user_id, page, COCKTAIL_PAGE_SIZE)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)
        except cs_exception.NotFoundError:
            raise exceptions.TelegramUserNotFoundError(f'Telegram user with ID {telegram_user_id} not found.')

        if not response.results:
            raise exceptions.CocktailNotFoundError("The external API returned an empty favorite cocktail list")

        favorite = response.results[0]
        text = self._build_cocktail_message_text(favorite.cocktail)
        reply_markup = self._build_favorite_cocktail_reply_markup(
            cocktail_id=favorite.cocktail.id,
            favorite_id=favorite.id,
            page=page,
            total_pages=response.total_pages
        )

        return TelegramMessage(text, reply_markup, ParseMode.HTML)

    @staticmethod
    def _build_cocktail_message_text(cocktail: Cocktail) -> str:
        template = jinja2.get_template('cocktail.html')

        return template.render(cocktail=cocktail)

    @staticmethod
    def _build_cocktail_reply_markup(cocktail_id: int, page: int, total_pages: int) -> InlinePaginationKeyboardMarkup:
        additional_buttons = [
            InlineKeyboardButton(text='Метод приготовления',
                                 callback_data=RecipeCallback(cocktail_id=cocktail_id).pack()),
            InlineKeyboardButton(text='Добавить в избранное',
                                 callback_data=AddFavoriteCallback(cocktail_id=cocktail_id).pack()),
        ]

        return InlinePaginationKeyboardMarkup(total_pages, page, [additional_buttons])

    @staticmethod
    def _build_favorite_cocktail_reply_markup(cocktail_id: int, favorite_id: int, page: int, total_pages: int):
        additional_buttons = [
            InlineKeyboardButton(text='Метод приготовления',
                                 callback_data=RecipeCallback(cocktail_id=cocktail_id).pack()),
            InlineKeyboardButton(text='Удалить из избранного',
                                 callback_data=RemoveFavorite(favorite_id=favorite_id).pack()),
        ]

        return InlinePaginationKeyboardMarkup(total_pages, page, [additional_buttons])

    async def get_cocktail_recipe_message(self, cocktail_id: int) -> TelegramMessage:
        """
        Получает сообщение, содержащее рецепт коктейля

        Args:
            cocktail_id: идентификатор коктейля

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            CocktailNotFoundError: возбуждаемое исключение в случае отсутствия коктейля с указанным cocktail_id
            CocktailRecipeNotFoundError: возбуждаемое исключение в случае отсутствия рецепта у коктейля
        """
        try:
            recipe = await self.api_client.get_cocktail_recipe(cocktail_id)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)
        except cs_exception.NotFoundError:
            raise exceptions.CocktailNotFoundError(f'Cocktail with ID {cocktail_id} not found.')

        if not recipe:
            raise exceptions.CocktailRecipeNotFoundError('There is no cocktail recipe yet')

        text = self._build_recipe_message_text(recipe)
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='back')]]
        )

        return TelegramMessage(text, reply_markup, ParseMode.HTML)

    @staticmethod
    def _build_recipe_message_text(recipe: List[CookingStage]) -> str:
        template = jinja2.get_template('recipe.html')

        return template.render(recipe=recipe)

    async def get_telegram_user_id(self, chat_id: int) -> int:
        """
        Получает идентификатор пользователя Telegram

        Args:
            chat_id: идентификатор чата пользователя Telegram

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            TelegramUserNotFoundError: возбуждаемое исключение в случае отсутствия пользователя с указанным chat_id

        Returns:
            Идентификатор пользователя Telegram
        """
        try:
            response = await self.api_client.get_telegram_users(chat_id)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)

        if not response.results:
            raise exceptions.TelegramUserNotFoundError(f'Telegram user with chat ID {chat_id} not found')

        return response.results[0].id

    async def create_telegram_user(self, chat_id: int) -> int:
        """
        Создает пользователя Telegram

        Args:
            chat_id: идентификатор чата пользователя Telegram

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            TelegramUserAlreadyExists: возбуждаемое исключение в случае наличия пользователя Telegram с указанным
                chat_id

        Returns:
            Идентификатор пользователя Telegram
        """
        try:
            telegram_user = await self.api_client.create_telegram_user(chat_id)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)
        except cs_exception.BadRequestError as ex:
            if not (chat_id_errors := ex.errors.get('chat_id')):
                raise
            already_exists_error = 'Telegram user with this Chat ID already exists.'
            for error in chat_id_errors:
                if error == already_exists_error:
                    raise exceptions.TelegramUserAlreadyExists(f'Telegram user with chat ID {chat_id} already exists.')
            raise

        return telegram_user.id

    async def add_cocktail_to_favorites(self, telegram_user_id: int, cocktail_id: int):
        """
        Добавляет коктейль в избранное пользователя Telegram

        Args:
            telegram_user_id: идентификатор пользователя Telegram
            cocktail_id: идентификатор коктейля

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            CocktailAlreadyInFavoritesError: возбуждаемое исключение в случае наличия коктейля в избранном пользователя
                Telegram
        """
        try:
            await self.api_client.add_cocktail_to_favorites(telegram_user_id, cocktail_id)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)
        except cs_exception.BadRequestError as ex:
            if not (non_field_errors := ex.errors.get('non_field_errors')):
                raise
            not_unique_set_error = 'The fields telegram_user, cocktail must make a unique set.'
            for error in non_field_errors:
                if error == not_unique_set_error:
                    raise exceptions.CocktailAlreadyInFavoritesError('Cocktail already in the Telegram user favorites')
            raise

    async def remove_cocktail_from_favorites(self, favorite_id: int):
        """
        Удаляет коктейль из избранного

        Args:
            favorite_id: идентификатор избранного

        Raises:
            ConnectionToExternalAPIError: возбуждаемое исключение в случае ошибки соединения с внешним API
            FavoriteNotFoundError: возбуждаемое исключение в случае отсутствия избранного с указанным favorite_id
        """
        try:
            await self.api_client.remove_cocktail_from_favorites(favorite_id)
        except cs_exception.TransportError as ex:
            raise exceptions.ConnectionToExternalAPIError(ex)
        except cs_exception.NotFoundError:
            raise exceptions.FavoriteNotFoundError(f'Favorites with ID {favorite_id} not found')
