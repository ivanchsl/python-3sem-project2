from aiogram import Bot, Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage
import logging


import config
from bot_router import router


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.BOT_API)
    storage = SQLStorage("fsm_storage.db")
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    dp.run_polling(bot)
