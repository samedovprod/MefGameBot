import asyncio
import logging
import os
import sys

import git
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

import db
from handlers import Handlers

logging.basicConfig(level=logging.INFO)
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = db.Database('database/mefmetrbot.db')
router = Router()
handlers = Handlers(router, db, bot)

dp.include_router(router)


def check_for_updates():
    repo = git.Repo(search_parent_directories=True)
    origin = repo.remotes.origin
    origin.fetch()
    commits_behind = list(repo.iter_commits('main..origin/main'))

    if commits_behind:
        print("Доступно обновление. Хотите установить? (y/n)")
        answer = input().lower()
        if answer == 'y':
            origin.pull()
            print("Обновления были установлены.")
            print("Список изменений:")
            for commit in commits_behind[::-1]:
                print(f"- {commit.summary}")
            print("Перезапустите бота.")
            return True
    return False


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
        update_available = check_for_updates()
        if update_available:
            sys.exit()
        asyncio.run(dp.start_polling(bot, skip_updates=True))
