from dataclasses import dataclass
from enum import Enum
from typing import Optional

from aiogram.types import InlineKeyboardMarkup


class ParseMode(str, Enum):
    HTML = 'HTML'
    MARKDOWN = 'Markdown'
    MARKDOWN_V2 = 'MarkdownV2'

    def __str__(self):
        return self.value


@dataclass
class TelegramMessage:
    text: str
    reply_markup: Optional[InlineKeyboardMarkup] = None
    parse_mode: Optional[ParseMode] = None
