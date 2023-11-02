import asyncio
import logging
import os
import subprocess
import sys

import git
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

import db
from handlers import Handlers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
database = db.Database('database/mefmetrbot.db')
router = Router()
handlers = Handlers(router, database, bot)

dp.include_router(router)


def check_for_updates():
    try:
        repo = git.Repo(search_parent_directories=True)
        origin = repo.remotes.origin
        origin.fetch()
        commits_behind = list(repo.iter_commits('main..origin/main'))

        if commits_behind:
            logger.info("Доступно обновление. Хотите установить? (y/n)")
            answer = input().lower()
            if answer == 'y':
                subprocess.run(["git", "reset", "--hard"], check=True)

                origin.pull()
                logger.info("Обновления были установлены.")
                for commit in commits_behind[::-1]:
                    logger.info(f"- {commit.summary}")
                logger.info("Перезапустите бота.")
                return True
    except Exception as e:
        logger.error(f"Ошибка проверки обновлений: {e}")
    return False


def giveadm(user_id):
    try:
        database.update_user(user_id, is_admin=1)
        logger.info(f"Пользователю с ID {user_id} были даны права администратора.")
    except Exception as e:
        logger.error(f"Ошибка выдачи административных прав: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == "giveadm":
        try:
            user_id = int(sys.argv[2])
            giveadm(user_id)
        except ValueError:
            logger.error("Ошибка: ID пользователя должно быть целым числом.")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
    else:
        update_available = check_for_updates()
        if update_available:
            sys.exit()
        asyncio.run(dp.start_polling(bot, skip_updates=True))
