from enum import Enum
from typing import Optional, Dict, Any, Union, List
from urllib.parse import urljoin

from httpx import AsyncClient
from pydantic import parse_raw_as

from bot.clients.cocktail_searcher.decorators import request_exception_handler
from bot.clients.cocktail_searcher.models import (
    PagePagination,
    Cocktail,
    CookingStage,
    TelegramUser,
    TelegramUserFavorite,
)
from config import settings


class HttpMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    def __str__(self):
        return self.value


class CocktailSearcherClient:
    """Клиент Cocktail Searcher API"""

    def __init__(self):
        self.base_url = settings.COCKTAIL_SEARCHER_URL
        self.cocktails_path = '/api/v1/cocktails/'
        self.cocktail_recipe_path = '/api/v1/cocktails/{id}/recipe/'
        self.favorites_path = '/api/v1/favorites/'
        self.telegram_user_path = '/api/v1/telegram-users/'
        self.telegram_user_favorites_path = '/api/v1/telegram-users/{id}/favorites/'

    async def get_cocktails(self,
                            search: Optional[str] = None,
                            page: Optional[int] = None,
                            page_size: Optional[int] = None) -> PagePagination[Cocktail]:
        """Получает коктейли

        Args:
            search: строка запроса поиска коктейлей
            page: номер страницы
            page_size: количество элементов на странице

        Returns:
            object: 
            Объект пагинации списка коктейлей

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
        """
        params = {'search': search, 'page': page, 'page_size': page_size}

        response = await self._request(HttpMethod.GET, urljoin(self.base_url, self.cocktails_path), params)

        return PagePagination[Cocktail].parse_raw(response)

    async def get_cocktail_recipe(self, cocktail_id: int) -> List[CookingStage]:
        """Получает рецепт приготовления коктейля

        Args:
            cocktail_id: идентификатор коктейля

        Returns:
            Список этапов приготовления рецепта

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
            NotFoundError: возбуждаемое исключение в случае попытки получения рецепта приготовления несуществующего коктейля
        """
        response = await self._request(
            HttpMethod.GET,
            urljoin(self.base_url, self.cocktail_recipe_path.format(id=cocktail_id))
        )

        return parse_raw_as(List[CookingStage], response)

    async def get_telegram_users(self,
                                 chat_id: Optional[int] = None,
                                 page: Optional[int] = None,
                                 page_size: Optional[int] = None) -> PagePagination[TelegramUser]:
        """Получает пользователей Telegram

        Args:
            chat_id: идентификатор чата пользователя Telegram
            page: номер страницы
            page_size: количество элементов на странице

        Returns:
            Объект пагинации списка пользователей Telegram

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
        """
        params = {'chat_id': chat_id, 'page': page, 'page_size': page_size}

        response = await self._request(HttpMethod.GET, urljoin(self.base_url, self.telegram_user_path), params)

        return PagePagination[TelegramUser].parse_raw(response)

    async def create_telegram_user(self, chat_id: int) -> TelegramUser:
        """Создает пользователя Telegram

        Args:
            chat_id: идентификатор чата пользователя Telegram

        Returns:
            Объект пользователя Telegram

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
            BadRequest: возбуждаемое исключение в случае создания пользователя Telegram с неуникальным chat_id
        """
        data = {'chat_id': chat_id}

        response = await self._request(HttpMethod.POST, urljoin(self.base_url, self.telegram_user_path), data=data)

        return TelegramUser.parse_raw(response)

    async def get_favorite_cocktails(self,
                                     telegram_user_id: int,
                                     page: Optional[int] = None,
                                     page_size: Optional[int] = None) -> PagePagination[TelegramUserFavorite]:
        """Получает избранные коктейли пользователя Telegram

        Args:
            telegram_user_id: идентификатор пользователя Telegram
            page: номер страницы
            page_size: количество элементов на странице

        Returns:
            Объект пагинации списка избранных коктейлей пользователя Telegram

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
            NotFoundError: возбуждаемое исключение в случае попытки получения избранных коктейлей несуществующего
                пользователя Telegram
        """
        params = {'page': page, 'page_size': page_size}

        response = await self._request(
            HttpMethod.GET,
            urljoin(self.base_url, self.telegram_user_favorites_path.format(id=telegram_user_id)),
            params
        )

        return PagePagination[TelegramUserFavorite].parse_raw(response)

    async def add_cocktail_to_favorites(self, telegram_user_id: int, cocktail_id: int):
        """Добавляет коктейль в избранное

        Args:
            telegram_user_id: идентификатор пользователя Telegram
            cocktail_id: идентификатор коктейля

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
            BadRequest: возбуждаемое исключение в случае попытки передачи несуществующих идентификаторов пользователя
                Telegram и коктейля, а также при попытке добавления в избранное уже находящимся в избранном коктейля
        """
        data = {'telegram_user': telegram_user_id, 'cocktail': cocktail_id}

        await self._request(HttpMethod.POST, urljoin(self.base_url, self.favorites_path), data=data)

    async def remove_cocktail_from_favorites(self, favorite_id: int):
        """Удаляет избранный коктейль

        Args:
            favorite_id: идентификатор избранного

        Raises:
            TransportError: возбуждаемое исключение в случае ошибки соединения
            NotFoundError: возбуждаемое исключение в случае попытки удаления несуществующей записи избранного
        """
        await self._request(HttpMethod.DELETE, urljoin(self.base_url, f'{self.favorites_path}{favorite_id}/'))

    @staticmethod
    @request_exception_handler
    async def _request(method: HttpMethod,
                       url: str,
                       params: Optional[Dict[str, Any]] = None,
                       data: Union[Dict[str, Any], str, None] = None) -> str:
        request_arguments = {
            'method': method,
            'url': url,
            'headers': {'Authorization': f'Token {settings.COCKTAIL_SEARCHER_API_TOKEN}'},
            'params': {key: value for key, value in params.items() if value is not None} if params else None
        }

        if isinstance(data, dict):
            request_arguments['json'] = data
        else:
            request_arguments['data'] = data

        async with AsyncClient() as client:
            response = await client.request(**request_arguments)
            response.raise_for_status()

            return response.text
