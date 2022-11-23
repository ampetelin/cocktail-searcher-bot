from typing import Any, Optional


class CocktailSearcherClientError(Exception):
    """Базовое исключение клиента Cocktail Searcher"""


class TransportError(CocktailSearcherClientError):
    """Базовый класс для всех исключений, возникающих на уровне Transport API"""


class ResponseError(CocktailSearcherClientError):
    """Базовая ошибка HTTP статуса"""


class BadRequestError(ResponseError):
    """Неправильный, некорректный запрос"""

    def __init__(self, message: Any, errors: Optional[dict]):
        self.errors = errors
        super().__init__(message)


class NotFoundError(ResponseError):
    """Не найдено"""
