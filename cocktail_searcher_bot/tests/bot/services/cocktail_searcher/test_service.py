from typing import List
from unittest.mock import create_autospec

import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydantic import parse_obj_as

from bot.clients.cocktail_searcher import exceptions as client_exceptions
from bot.clients.cocktail_searcher.client import CocktailSearcherClient
from bot.clients.cocktail_searcher.models import (
    PagePagination,
    Cocktail,
    TelegramUserFavorite,
    CookingStage,
    TelegramUser,
)
from bot.services.cocktail_searcher import exceptions
from bot.services.cocktail_searcher.dtos import TelegramMessage
from bot.services.cocktail_searcher.service import CocktailSearcherService, COCKTAIL_PAGE_SIZE
from tests.bot.clients.cocktail_searcher import mocks


@pytest.mark.asyncio
class TestCocktailSearcherService:
    def setup_class(self):
        self.service = CocktailSearcherService()
        self.service.api_client = create_autospec(CocktailSearcherClient)

    def setup_method(self):
        self.service.api_client.reset_mock(return_value=True, side_effect=True)

    @pytest.mark.parametrize('payload', [{'search': None}, {'search': 'test'}, {'search': 'test', 'page': 2}])
    async def test_get_cocktail_message(self, payload):
        self.service.api_client.get_cocktails.return_value = PagePagination[Cocktail].parse_obj(mocks.COCKTAIL_RESPONSE)

        page = payload.get('page', 1)
        response = await self.service.get_cocktail_message(**payload)

        self.service.api_client.get_cocktails.assert_called_once_with(
            **{'page': page, 'page_size': COCKTAIL_PAGE_SIZE, **payload}
        )
        assert isinstance(response, TelegramMessage)
        parsed_mock = PagePagination[Cocktail].parse_obj(mocks.COCKTAIL_RESPONSE)
        cocktail = parsed_mock.results[0]
        assert response.text == self.service._build_cocktail_message_text(cocktail=cocktail)
        assert response.reply_markup == self.service._build_cocktail_reply_markup(
            cocktail_id=cocktail.id,
            page=page,
            total_pages=parsed_mock.total_pages
        )
        assert response.parse_mode == 'HTML'

    async def test_get_cocktail_message_cocktail_not_found(self):
        self.service.api_client.get_cocktails.return_value = PagePagination[Cocktail].parse_obj(
            mocks.PAGINATION_EMPTY_RESPONSE_RESULT
        )
        search_query = 'test'
        page = 1

        with pytest.raises(exceptions.CocktailNotFoundError):
            await self.service.get_cocktail_message(search=search_query, page=page)
        self.service.api_client.get_cocktails.assert_called_once_with(search_query, page, COCKTAIL_PAGE_SIZE)

    async def test_get_cocktail_connection_error(self):
        self.service.api_client.get_cocktails.side_effect = client_exceptions.TransportError
        search_query = 'test'
        page = 1

        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.get_cocktail_message(search=search_query, page=page)
        self.service.api_client.get_cocktails.assert_called_once_with(search_query, page, COCKTAIL_PAGE_SIZE)

    async def test_get_favorite_cocktail_message(self):
        self.service.api_client.get_favorite_cocktails.return_value = PagePagination[TelegramUserFavorite].parse_obj(
            mocks.TELEGRAM_USER_FAVORITE_RESPONSE
        )
        page = telegram_user_id = 1
        response = await self.service.get_favorite_cocktail_message(telegram_user_id=telegram_user_id)

        self.service.api_client.get_favorite_cocktails.assert_called_once_with(
            telegram_user_id, page, COCKTAIL_PAGE_SIZE
        )
        assert isinstance(response, TelegramMessage)
        parsed_mock = PagePagination[TelegramUserFavorite].parse_obj(mocks.TELEGRAM_USER_FAVORITE_RESPONSE)
        favorite = parsed_mock.results[0]
        assert response.text == self.service._build_cocktail_message_text(cocktail=favorite.cocktail)
        assert response.reply_markup == self.service._build_favorite_cocktail_reply_markup(
            cocktail_id=favorite.cocktail.id,
            favorite_id=favorite.id,
            page=page,
            total_pages=parsed_mock.total_pages
        )
        assert response.parse_mode == 'HTML'

    async def test_get_favorite_cocktail_message_telegram_user_not_found(self):
        self.service.api_client.get_favorite_cocktails.side_effect = client_exceptions.NotFoundError
        page = telegram_user_id = 1

        with pytest.raises(exceptions.TelegramUserNotFoundError):
            await self.service.get_favorite_cocktail_message(telegram_user_id=telegram_user_id)
        self.service.api_client.get_favorite_cocktails.assert_called_once_with(
            telegram_user_id, page, COCKTAIL_PAGE_SIZE
        )

    async def test_get_favorite_cocktail_message_cocktails_not_found(self):
        self.service.api_client.get_favorite_cocktails.return_value = PagePagination[TelegramUserFavorite].parse_obj(
            mocks.PAGINATION_EMPTY_RESPONSE_RESULT
        )
        page = telegram_user_id = 1
        with pytest.raises(exceptions.CocktailNotFoundError):
            await self.service.get_favorite_cocktail_message(telegram_user_id=telegram_user_id)
        self.service.api_client.get_favorite_cocktails.assert_called_once_with(
                telegram_user_id, page, COCKTAIL_PAGE_SIZE
        )

    async def test_get_favorite_cocktail_message_connection_error(self):
        self.service.api_client.get_favorite_cocktails.side_effect = client_exceptions.TransportError
        page = telegram_user_id = 1
        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.get_favorite_cocktail_message(telegram_user_id=telegram_user_id)
        self.service.api_client.get_favorite_cocktails.assert_called_once_with(
            telegram_user_id, page, COCKTAIL_PAGE_SIZE
        )

    async def test_get_cocktail_recipe_message(self):
        self.service.api_client.get_cocktail_recipe.return_value = parse_obj_as(
            List[CookingStage], mocks.COCKTAIL_RECIPE_RESPONSE
        )
        cocktail_id = 1
        response = await self.service.get_cocktail_recipe_message(cocktail_id=cocktail_id)

        self.service.api_client.get_cocktail_recipe.assert_called_once_with(cocktail_id)
        assert isinstance(response, TelegramMessage)
        recipe = parse_obj_as(List[CookingStage], mocks.COCKTAIL_RECIPE_RESPONSE)
        assert response.text == self.service._build_recipe_message_text(recipe=recipe)
        assert response.reply_markup == InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='back')]]
        )
        assert response.parse_mode == 'HTML'

    async def test_get_cocktail_recipe_message_cocktail_not_found(self):
        self.service.api_client.get_cocktail_recipe.side_effect = client_exceptions.NotFoundError
        cocktail_id = 1

        with pytest.raises(exceptions.CocktailNotFoundError):
            await self.service.get_cocktail_recipe_message(cocktail_id=cocktail_id)
        self.service.api_client.get_cocktail_recipe.assert_called_once_with(cocktail_id)

    async def test_get_cocktail_recipe_message_recipe_not_found(self):
        self.service.api_client.get_cocktail_recipe.return_value = []
        cocktail_id = 1

        with pytest.raises(exceptions.CocktailRecipeNotFoundError):
            await self.service.get_cocktail_recipe_message(cocktail_id=cocktail_id)
        self.service.api_client.get_cocktail_recipe.assert_called_once_with(cocktail_id)

    async def test_get_cocktail_recipe_message_connection_error(self):
        self.service.api_client.get_cocktail_recipe.side_effect = client_exceptions.TransportError
        cocktail_id = 1
        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.get_cocktail_recipe_message(cocktail_id=cocktail_id)
        self.service.api_client.get_cocktail_recipe.assert_called_once_with(cocktail_id)

    async def test_get_telegram_user_id(self):
        self.service.api_client.get_telegram_users.return_value = PagePagination[TelegramUser].parse_obj(
            mocks.TELEGRAM_USER_RESPONSE
        )
        chat_id = 12345
        response = await self.service.get_telegram_user_id(chat_id=chat_id)

        self.service.api_client.get_telegram_users.assert_called_once_with(chat_id)
        assert isinstance(response, int)
        assert response == 1

    async def test_get_telegram_user_id_not_found(self):
        self.service.api_client.get_telegram_users.return_value = PagePagination[TelegramUser].parse_obj(
            mocks.PAGINATION_EMPTY_RESPONSE_RESULT
        )
        chat_id = 12345
        with pytest.raises(exceptions.TelegramUserNotFoundError):
            await self.service.get_telegram_user_id(chat_id=chat_id)
        self.service.api_client.get_telegram_users.assert_called_once_with(chat_id)

    async def test_get_telegram_user_id_connection_error(self):
        self.service.api_client.get_telegram_users.side_effect = client_exceptions.TransportError
        chat_id = 12345
        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.get_telegram_user_id(chat_id=chat_id)
        self.service.api_client.get_telegram_users.assert_called_once_with(chat_id)

    async def test_create_telegram_user(self):
        self.service.api_client.create_telegram_user.return_value = TelegramUser.parse_obj(
            mocks.CREATE_TELEGRAM_USER_RESPONSE
        )
        chat_id = 12345
        response = await self.service.create_telegram_user(chat_id=chat_id)

        self.service.api_client.create_telegram_user.assert_called_once_with(chat_id)
        assert isinstance(response, int)
        assert response == 1

    async def test_create_telegram_user_already_exists(self):
        self.service.api_client.create_telegram_user.side_effect = client_exceptions.BadRequestError(
            message='Bad request',
            errors=mocks.CREATE_TELEGRAM_USER_BAD_REQUEST_RESPONSE
        )
        chat_id = 12345

        with pytest.raises(exceptions.TelegramUserAlreadyExists):
            await self.service.create_telegram_user(chat_id=chat_id)
        self.service.api_client.create_telegram_user.assert_called_once_with(chat_id)

    async def test_create_telegram_user_connection_error(self):
        self.service.api_client.create_telegram_user.side_effect = client_exceptions.TransportError
        chat_id = 12345
        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.create_telegram_user(chat_id=chat_id)
        self.service.api_client.create_telegram_user.assert_called_once_with(chat_id)

    async def test_add_cocktail_to_favorites(self):
        telegram_user_id = cocktail_id = 1
        await self.service.add_cocktail_to_favorites(telegram_user_id=telegram_user_id, cocktail_id=cocktail_id)

        response = self.service.api_client.add_cocktail_to_favorites.assert_called_once_with(
            telegram_user_id, cocktail_id
        )
        assert response is None

    async def test_add_cocktail_to_favorites_cocktail_already_in_favorites(self):
        self.service.api_client.add_cocktail_to_favorites.side_effect = client_exceptions.BadRequestError(
            message='Bad request',
            errors=mocks.ADD_COCKTAIL_TO_FAVORITES_COCKTAIL_BAD_REQUEST_RESPONSE
        )
        telegram_user_id = cocktail_id = 1

        with pytest.raises(exceptions.CocktailAlreadyInFavoritesError):
            await self.service.add_cocktail_to_favorites(telegram_user_id=telegram_user_id, cocktail_id=cocktail_id)
        self.service.api_client.add_cocktail_to_favorites.assert_called_once_with(telegram_user_id, cocktail_id)

    async def test_add_cocktail_to_favorites_connection_error(self):
        self.service.api_client.add_cocktail_to_favorites.side_effect = client_exceptions.TransportError
        telegram_user_id = cocktail_id = 1

        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.add_cocktail_to_favorites(telegram_user_id=telegram_user_id, cocktail_id=cocktail_id)
        self.service.api_client.add_cocktail_to_favorites.assert_called_once_with(telegram_user_id, cocktail_id)

    async def test_remove_cocktail_from_favorites(self):
        favorite_id = 1
        await self.service.remove_cocktail_from_favorites(favorite_id=favorite_id)

        self.service.api_client.remove_cocktail_from_favorites.assert_called_once_with(favorite_id)

    async def test_remove_cocktail_from_favorites_not_found(self):
        self.service.api_client.remove_cocktail_from_favorites.side_effect = client_exceptions.NotFoundError
        favorite_id = 1

        with pytest.raises(exceptions.FavoriteNotFoundError):
            await self.service.remove_cocktail_from_favorites(favorite_id=favorite_id)
        self.service.api_client.remove_cocktail_from_favorites.assert_called_once_with(favorite_id)

    async def test_remove_cocktail_from_favorites_connection_error(self):
        self.service.api_client.remove_cocktail_from_favorites.side_effect = client_exceptions.TransportError
        favorite_id = 1

        with pytest.raises(exceptions.ConnectionToExternalAPIError):
            await self.service.remove_cocktail_from_favorites(favorite_id=favorite_id)
        self.service.api_client.remove_cocktail_from_favorites.assert_called_once_with(favorite_id)
