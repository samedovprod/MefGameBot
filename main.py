import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

import db
from handlers import Handlers
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = db.Database('database/mefmetrbot.db')
router = Router()
handlers = Handlers(router, db, bot)

dp.include_router(router)


def giveadm(id):
    db.update_user(id, is_admin=1)
    print(f"Пользователю с ID {id} были даны права администратора.")


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == "giveadm":
        try:
            id = int(sys.argv[2])
            giveadm(id)
        except ValueError:
            print("Ошибка: ID пользователя должно быть целым числом.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    else:
        asyncio.run(dp.start_polling(bot, skip_updates=True))
