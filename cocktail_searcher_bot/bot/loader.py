from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.commands import router as commands_router
from bot.handlers.exceptions import router as exception_router
from bot.handlers.favorites import router as favorites_router
from bot.handlers.search import router as search_router
from config import settings

bot = Bot(token=settings.TELEGRAM_API_TOKEN)

dispatcher = Dispatcher(storage=MemoryStorage())
dispatcher.include_router(commands_router)
dispatcher.include_router(search_router)
dispatcher.include_router(favorites_router)
dispatcher.include_router(exception_router)
