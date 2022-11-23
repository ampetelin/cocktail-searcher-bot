class CocktailSearcherServiceError(Exception):
    """Базовое исключение сервиса Cocktail Searcher"""


class ConnectionToExternalAPIError(CocktailSearcherServiceError):
    """Ошибка соединения с внешним API"""


class CocktailNotFoundError(CocktailSearcherServiceError):
    """Коктейль не найден"""


class CocktailAlreadyInFavoritesError(CocktailSearcherServiceError):
    """Коктейль уже есть в избранном"""


class CocktailRecipeNotFoundError(CocktailSearcherServiceError):
    """Рецепт коктейля не найден"""


class CategoryNotFoundError(CocktailSearcherServiceError):
    """Категории не найдены"""


class TelegramUserNotFoundError(CocktailSearcherServiceError):
    """Пользователь Telegram не найден"""


class TelegramUserAlreadyExists(CocktailSearcherServiceError):
    """Пользователь Telegram уже существует"""


class FavoriteNotFoundError(CocktailSearcherServiceError):
    """Избранное не найдено"""
