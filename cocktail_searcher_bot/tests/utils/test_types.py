import pytest
from aiogram.types import InlineKeyboardButton

from utils.aiogram.types import InlinePaginationKeyboardMarkup, PaginationCallback


class TestInclinePaginationKeyboardMarkup:
    def test_single_page_pagination(self):
        markup = InlinePaginationKeyboardMarkup(page_count=1, current_page=1)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        assert markup.inline_keyboard == [[]]

    @pytest.mark.parametrize('current_page', [1, 2, 3])
    def test_more_than_five_pages_pagination_left_state(self, current_page):
        page_count = 10
        markup = InlinePaginationKeyboardMarkup(page_count=page_count, current_page=current_page)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        inline_keyboard = markup.inline_keyboard[0]
        assert len(inline_keyboard) == 5
        for i, button in enumerate(inline_keyboard[:4], start=1):
            assert PaginationCallback.unpack(button.callback_data).page == i
        assert PaginationCallback.unpack(inline_keyboard[-1].callback_data).page == page_count

    @pytest.mark.parametrize('current_page', [4, 5, 6, 7, 8])
    def test_more_than_five_pages_pagination_center_state(self, current_page):
        page_count = 10
        markup = InlinePaginationKeyboardMarkup(page_count=page_count, current_page=current_page)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        inline_keyboard = markup.inline_keyboard[0]
        assert len(inline_keyboard) == 5
        assert PaginationCallback.unpack(inline_keyboard[0].callback_data).page == 1
        for i, button in enumerate(inline_keyboard[1:4], start=current_page - 1):
            assert PaginationCallback.unpack(button.callback_data).page == i
        assert PaginationCallback.unpack(inline_keyboard[-1].callback_data).page == page_count

    @pytest.mark.parametrize('current_page', [9, 10])
    def test_more_than_five_pages_pagination_right_state(self, current_page):
        page_count = 10
        markup = InlinePaginationKeyboardMarkup(page_count=page_count, current_page=current_page)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        inline_keyboard = markup.inline_keyboard[0]
        assert len(inline_keyboard) == 5
        assert PaginationCallback.unpack(inline_keyboard[0].callback_data).page == 1
        for i, button in enumerate(inline_keyboard[1:], start=page_count - 3):
            assert PaginationCallback.unpack(button.callback_data).page == i

    def test_less_than_five_pages_pagination(self):
        page_count = 5
        markup = InlinePaginationKeyboardMarkup(page_count=page_count, current_page=1)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        inline_keyboard = markup.inline_keyboard[0]
        assert len(inline_keyboard) == page_count
        for i, button in enumerate(inline_keyboard, start=1):
            assert PaginationCallback.unpack(button.callback_data).page == i

    def test_current_page_exceeds_page_count(self):
        page_count = 1
        current_page = 2

        with pytest.raises(ValueError):
            InlinePaginationKeyboardMarkup(page_count=page_count, current_page=current_page)

    def test_adding_additional_buttons(self):
        additional_buttons = [[InlineKeyboardButton(text='text', callback_data='test')]]
        markup = InlinePaginationKeyboardMarkup(page_count=1, current_page=1, additional_buttons=additional_buttons)

        assert isinstance(markup, InlinePaginationKeyboardMarkup)
        assert markup.inline_keyboard == additional_buttons
