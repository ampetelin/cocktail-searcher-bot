from http import HTTPStatus
from typing import List
from urllib.parse import urljoin

import pytest
from pydantic import parse_obj_as

from bot.clients.cocktail_searcher import exceptions
from bot.clients.cocktail_searcher.client import CocktailSearcherClient
from bot.clients.cocktail_searcher.models import (
    PagePagination,
    Cocktail,
    CookingStage,
    TelegramUser,
    TelegramUserFavorite,
)
from tests.bot.clients.cocktail_searcher import mocks
from tests.helpers import add_query_params_in_url


@pytest.mark.asyncio
class TestCocktailSearcherClient:
    def setup_class(self):
        self.client = CocktailSearcherClient()

    @pytest.mark.parametrize('response_mock', [mocks.COCKTAIL_RESPONSE, mocks.PAGINATION_EMPTY_RESPONSE_RESULT])
    @pytest.mark.parametrize('payload', [{}, {'search': 'test', 'page': 2, 'page_size': 1}])
    async def test_get_cocktails(self, httpx_mock, response_mock, payload):
        url = urljoin(self.client.base_url, self.client.cocktails_path)
        httpx_mock.add_response(
            url=add_query_params_in_url(url=url, query_params=payload),
            status_code=HTTPStatus.OK,
            json=response_mock
        )
        response = await self.client.get_cocktails(**payload)

        assert isinstance(response, PagePagination[Cocktail])
        assert response == PagePagination[Cocktail].parse_obj(response_mock)

    async def test_get_cocktails_transport_error(self, httpx_mock):
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.cocktails_path),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.get_cocktails()

    async def test_get_cocktail_recipe(self, httpx_mock):
        cocktail_id = 1
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.cocktail_recipe_path.format(id=cocktail_id)),
            status_code=HTTPStatus.OK,
            json=mocks.COCKTAIL_RECIPE_RESPONSE
        )
        response = await self.client.get_cocktail_recipe(cocktail_id=cocktail_id)

        assert isinstance(response, list)
        assert all(isinstance(cooking_stage, CookingStage) for cooking_stage in response)
        assert response == parse_obj_as(List[CookingStage], mocks.COCKTAIL_RECIPE_RESPONSE)

    async def test_get_cocktail_recipe_cocktail_not_found(self, httpx_mock):
        cocktail_id = 1
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.cocktail_recipe_path.format(id=cocktail_id)),
            status_code=HTTPStatus.NOT_FOUND
        )
        with pytest.raises(exceptions.NotFoundError):
            await self.client.get_cocktail_recipe(cocktail_id=cocktail_id)

    async def test_get_cocktail_recipe_transport_error(self, httpx_mock):
        cocktail_id = 1
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.cocktail_recipe_path.format(id=cocktail_id)),
            exception=mocks.TRANSPORT_EXCEPTION)
        with pytest.raises(exceptions.TransportError):
            await self.client.get_cocktail_recipe(cocktail_id=cocktail_id)

    @pytest.mark.parametrize('response_mock', [mocks.TELEGRAM_USER_RESPONSE, mocks.PAGINATION_EMPTY_RESPONSE_RESULT])
    @pytest.mark.parametrize('payload', [{}, {'chat_id': 12345, 'page': 2, 'page_size': 1}])
    async def test_get_telegram_users(self, httpx_mock, response_mock, payload):
        url = urljoin(self.client.base_url, self.client.telegram_user_path)
        httpx_mock.add_response(
            url=add_query_params_in_url(url=url, query_params=payload),
            status_code=HTTPStatus.OK,
            json=response_mock
        )
        response = await self.client.get_telegram_users(**payload)

        assert isinstance(response, PagePagination[TelegramUser])
        assert response == PagePagination[TelegramUser].parse_obj(response_mock)

    async def test_get_telegram_user_transport_error(self, httpx_mock):
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.telegram_user_path),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.get_telegram_users()

    async def test_create_telegram_user(self, httpx_mock):
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.telegram_user_path),
            status_code=HTTPStatus.CREATED,
            json=mocks.CREATE_TELEGRAM_USER_RESPONSE
        )
        response = await self.client.create_telegram_user(chat_id=12345)

        assert isinstance(response, TelegramUser)
        assert response == TelegramUser.parse_obj(mocks.CREATE_TELEGRAM_USER_RESPONSE)

    async def test_create_telegram_user_bad_request(self, httpx_mock):
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.telegram_user_path),
            status_code=HTTPStatus.BAD_REQUEST,
            json=mocks.CREATE_TELEGRAM_USER_BAD_REQUEST_RESPONSE
        )
        with pytest.raises(exceptions.BadRequestError):
            await self.client.create_telegram_user(chat_id=12345)

    async def test_create_telegram_user_transport_error(self, httpx_mock):
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.telegram_user_path),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.create_telegram_user(chat_id=12345)

    @pytest.mark.parametrize('pagination_payload', [{}, {'page': 2, 'page_size': 1}])
    async def test_get_favorite_cocktails(self, httpx_mock, pagination_payload):
        telegram_user_id = 1
        url = urljoin(self.client.base_url, self.client.telegram_user_favorites_path.format(id=telegram_user_id))
        httpx_mock.add_response(
            url=add_query_params_in_url(url=url, query_params=pagination_payload),
            status_code=HTTPStatus.OK,
            json=mocks.TELEGRAM_USER_FAVORITE_RESPONSE
        )
        response = await self.client.get_favorite_cocktails(telegram_user_id=telegram_user_id, **pagination_payload)

        assert isinstance(response, PagePagination[TelegramUserFavorite])
        assert response == PagePagination[TelegramUserFavorite].parse_obj(mocks.TELEGRAM_USER_FAVORITE_RESPONSE)

    async def test_get_favorite_cocktails_not_found(self, httpx_mock):
        telegram_user_id = 1
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.telegram_user_favorites_path.format(id=telegram_user_id)),
            status_code=HTTPStatus.NOT_FOUND,
        )
        with pytest.raises(exceptions.NotFoundError):
            await self.client.get_favorite_cocktails(telegram_user_id=telegram_user_id)

    async def test_get_favorite_cocktail_transport_error(self, httpx_mock):
        telegram_user_id = 1
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.telegram_user_favorites_path.format(id=telegram_user_id)),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.get_favorite_cocktails(telegram_user_id=1)

    async def test_add_cocktail_to_favorites(self, httpx_mock):
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.favorites_path),
            status_code=HTTPStatus.CREATED
        )
        await self.client.add_cocktail_to_favorites(telegram_user_id=1, cocktail_id=1)

    async def test_add_cocktail_to_favorites_bad_request(self, httpx_mock):
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, self.client.favorites_path),
            status_code=HTTPStatus.BAD_REQUEST,
            json=mocks.ADD_COCKTAIL_TO_FAVORITES_COCKTAIL_BAD_REQUEST_RESPONSE
        )
        with pytest.raises(exceptions.BadRequestError):
            await self.client.add_cocktail_to_favorites(telegram_user_id=1, cocktail_id=1)

    async def test_add_cocktail_to_favorites_transport_error(self, httpx_mock):
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, self.client.favorites_path),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.add_cocktail_to_favorites(telegram_user_id=1, cocktail_id=1)

    async def test_remove_cocktail_from_favorites(self, httpx_mock):
        favorite_id = 1
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, f'{self.client.favorites_path}{favorite_id}/'),
            status_code=HTTPStatus.NO_CONTENT
        )
        await self.client.remove_cocktail_from_favorites(favorite_id=favorite_id)

    async def test_remove_cocktail_from_favorites_not_found(self, httpx_mock):
        favorite_id = 1
        httpx_mock.add_response(
            url=urljoin(self.client.base_url, f'{self.client.favorites_path}{favorite_id}/'),
            status_code=HTTPStatus.NOT_FOUND
        )
        with pytest.raises(exceptions.NotFoundError):
            await self.client.remove_cocktail_from_favorites(favorite_id=favorite_id)

    async def test_remove_cocktail_from_favorites_transport_error(self, httpx_mock):
        favorite_id = 1
        httpx_mock.add_exception(
            url=urljoin(self.client.base_url, f'{self.client.favorites_path}{favorite_id}/'),
            exception=mocks.TRANSPORT_EXCEPTION
        )
        with pytest.raises(exceptions.TransportError):
            await self.client.remove_cocktail_from_favorites(favorite_id=favorite_id)
