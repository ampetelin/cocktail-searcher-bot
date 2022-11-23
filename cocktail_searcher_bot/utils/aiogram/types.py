from enum import Enum
from typing import List, Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class PageLabelPattern(str, Enum):
    FIRST_PAGE = '« {}'
    PREVIOUS_PAGE = '‹ {}'
    CURRENT_PAGE = '· {} ·'
    NEXT_PAGE = '{} ›'
    LAST_PAGE = '{} »'


class PaginationCallback(CallbackData, prefix='pagination'):
    page: int


class InlinePaginationKeyboardMarkup(InlineKeyboardMarkup):
    """Класс разметки клавиатуры, реализующий страничную пагинацию

    Attributes:
        page_count: общее количество страниц пагинации
        current_page: текущая страница пагинации
        additional_buttons: дополнительные кнопки клавиатуры, добавляемые перед кнопками пагинации
    """
    def __init__(self,
                 page_count: int,
                 current_page: int,
                 additional_buttons: Optional[List[List[InlineKeyboardButton]]] = None):
        if current_page > page_count:
            raise ValueError('The current pagination page cannot be more than the number of pagination pages')

        if additional_buttons is None:
            additional_buttons = []
        pagination_buttons = self._build_pagination_buttons(page_count, current_page)
        additional_buttons.append(pagination_buttons)

        super().__init__(inline_keyboard=additional_buttons)

    @staticmethod
    def _build_pagination_buttons(page_count: int, current_page: int) -> List[InlineKeyboardButton]:
        buttons = []
        if 1 < page_count <= 5:
            buttons = [InlineKeyboardButton(text=str(i), callback_data=PaginationCallback(page=i).pack())
                       for i in range(1, page_count + 1)]
        elif page_count > 5:
            if current_page <= 3:
                buttons.extend([InlineKeyboardButton(text=str(i), callback_data=PaginationCallback(page=i).pack())
                                for i in range(1, 4)])
                buttons.append(InlineKeyboardButton(text=PageLabelPattern.NEXT_PAGE.value.format(4),
                                                    callback_data=PaginationCallback(page=4).pack()))
                buttons.append(InlineKeyboardButton(text=PageLabelPattern.LAST_PAGE.value.format(page_count),
                                                    callback_data=PaginationCallback(page=page_count).pack()))
            elif current_page <= page_count - 3:
                previous_page = current_page - 1
                next_page = current_page + 1
                buttons = [
                    InlineKeyboardButton(text=PageLabelPattern.FIRST_PAGE.value.format(1),
                                         callback_data=PaginationCallback(page=1).pack()),
                    InlineKeyboardButton(text=PageLabelPattern.PREVIOUS_PAGE.value.format(previous_page),
                                         callback_data=PaginationCallback(page=previous_page).pack()),
                    InlineKeyboardButton(text=PageLabelPattern.CURRENT_PAGE.value.format(current_page),
                                         callback_data=PaginationCallback(page=current_page).pack()),
                    InlineKeyboardButton(text=PageLabelPattern.NEXT_PAGE.value.format(next_page),
                                         callback_data=PaginationCallback(page=next_page).pack()),
                    InlineKeyboardButton(text=PageLabelPattern.LAST_PAGE.value.format(page_count),
                                         callback_data=PaginationCallback(page=page_count).pack()),
                ]
            else:
                previous_page = page_count - 3
                buttons = [InlineKeyboardButton(text=PageLabelPattern.FIRST_PAGE.value.format(1),
                                                callback_data=PaginationCallback(page=1).pack()),
                           InlineKeyboardButton(text=PageLabelPattern.PREVIOUS_PAGE.value.format(previous_page),
                                                callback_data=PaginationCallback(page=previous_page).pack())]
                buttons.extend([InlineKeyboardButton(text=str(i), callback_data=PaginationCallback(page=i).pack())
                                for i in range(page_count - 2, page_count + 1)])

        current_page_text = str(current_page)
        for button in buttons:
            if button.text == current_page_text:
                button.text = PageLabelPattern.CURRENT_PAGE.value.format(current_page)

        return buttons
