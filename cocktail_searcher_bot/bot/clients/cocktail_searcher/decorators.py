import json
from http import HTTPStatus

from httpx import TransportError, HTTPStatusError, HTTPError

from bot.clients.cocktail_searcher import exceptions


def request_exception_handler(func):
    """Обработчик исключений HTTP-запросов"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TransportError as ex:
            raise exceptions.TransportError(ex)
        except HTTPStatusError as ex:
            if ex.response.status_code == HTTPStatus.BAD_REQUEST:
                raise exceptions.BadRequestError(ex, errors=json.loads(ex.response.text))
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise exceptions.NotFoundError(ex)
            raise exceptions.ResponseError(ex)
        except HTTPError as ex:
            raise exceptions.CocktailSearcherClientError(ex)

    return wrapper
