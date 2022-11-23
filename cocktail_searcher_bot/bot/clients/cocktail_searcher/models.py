from typing import List, TypeVar, Generic

from pydantic import BaseModel, AnyHttpUrl
from pydantic.generics import GenericModel

PydanticModel = TypeVar('PydanticModel')


class Category(BaseModel):
    """Категория коктейля"""
    name: str


class Composition(BaseModel):
    """Состав коктейля"""
    ingredient_name: str
    amount: int
    unit_name: str


class CookingStage(BaseModel):
    """Этап рецепта приготовления"""
    stage: int
    action: str


class Cocktail(BaseModel):
    """Коктейль"""
    id: int
    name: str
    image_url: AnyHttpUrl
    categories: List[Category]
    composition: List[Composition]


class TelegramUser(BaseModel):
    """Пользователь Telegram"""
    id: int
    chat_id: int


class TelegramUserFavorite(BaseModel):
    """Избранное пользователя Telegram"""
    id: int
    cocktail: Cocktail


class PagePagination(GenericModel, Generic[PydanticModel]):
    """Постраничная пагинация"""
    count: int
    total_pages: int
    results: List[PydanticModel]
