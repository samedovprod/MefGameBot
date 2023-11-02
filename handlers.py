import logging
import random
from datetime import datetime, timedelta

from aiogram import types
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated


class Handlers:
    def __init__(self, router, db, bot):
        self.router = router
        self.db = db
        self.bot = bot
        self.command_mapping = {
            'start': self.start_command,
            'rules': self.rules_command,
            'admin': self.monkey_alarm,
            'getadmin': self.monkey_alarm,
            'free': self.monkey_alarm,
            'freeadmin': self.monkey_alarm,
            'help': self.help_command,
            'profile': self.profile_command,
            'drug': self.drug_command,
            'top': self.top_command,
            'take': self.take_command,
            'casino': self.casino,
            'give': self.give_command,
            'clancreate': self.create_clan,
            'deposit': self.deposit,
            'withdraw': self.withdraw,
            'clantop': self.clan_top,
            'clanbalance': self.clanbalance,
            'clanwar': self.clanwar,
            'clanowner': self.clan_owner,
            'claninfo': self.claninfo,
            'clanmembers': self.clanmembers,
            'claninvite': self.claninvite,
            'clankick': self.clankick,
            'clanleave': self.clanleave,
            'clandisband': self.clandisband,
            'clanaccept': self.clanaccept,
            'clandecline': self.clandecline,
            'find': self.drug_find,
            'banuser': self.banuser_command,
            'unbanuser': self.unbanuser_command,
            'setdrugs': self.setdrugs_command,
            'usercount': self.usercount,
            'broadcast': self.cmd_broadcast_start,

        }
        self.register_handlers()

    def register_handlers(self):
        for command, handler in self.command_mapping.items():
            self.router.message(Command(command))(handler)
        self.router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))(self.add_chat)

    @staticmethod
    async def monkey_alarm(message):
        await message.reply("🚨 *MONKEY ALARM*", parse_mode='markdown')

    @staticmethod
    async def start_command(message):
        await message.reply(
            "👋 *Здарова шныр*, этот бот сделан для того, чтобы *считать* сколько *грамм мефедрончика* ты снюхал")

    @staticmethod
    async def rules_command(message: types.Message):
        await message.reply('''Правила пользования MefGameBot:
                          *1) Мультиаккаунтинг - бан навсегда и обнуление всех аккаунтов *
                          *2) Использование любых уязвимостей бота - бан до исправления и возможное обнуление*
                          *3) Запрещена реклама через топ кланов и топ юзеров - выговор, после бан с обнулением*
                          *4) Запрещена продажа валюты между игроками - обнуление и бан*

                          *Бот не имеет никакого отношения к реальности. Все совпадения случайны. 
                          Создатели не пропагандируют наркотики и против их распространения и употребления. 
                          Употребление, хранение и продажа является уголовно наказуемой*
                          *Сообщить о багах вы можете администраторам* (*команда* `/about`)''', parse_mode='markdown')

    @staticmethod
    async def help_command(message: types.Message):
        await message.reply('''Все команды бота:

                `/drug` - *принять мефик*
                `/top` - *топ торчей мира*
                `/take` - *спиздить мефик у ближнего*
                `/give` - *поделиться мефиком*
                `/casino` - *казино*
                `/find` - *сходить за кладом*
                `/about` - *узнать подробнее о боте*
                `/clancreate` - *создать клан*
                `/deposit` - *пополнить баланс клана*
                `/withdraw` - *вывести средства с клана*
                `/clantop` - *топ 10 кланов по состоянию баланса*
                `/clanbalance` - *баланс клана*
                `/claninfo` - *о клане*
                `/claninvite` - *пригласить в клан*
                `/clankick` - *кикнуть из клана*
                `/clanaccept` - *принять приглашение в клан*
                `/clandecline` - *отказаться от приглашения в клан*
                `/clanleave` - *добровольно выйти из клана*
                `/clandisband` - *распустить клан*
                    ''', parse_mode='markdown')

    async def add_chat(self, update: ChatMemberUpdated):
        logging.info(f"Обрабатывается update: {update}")
        if update.new_chat_member.user.id == self.bot.id and update.new_chat_member.status == 'member':
            logging.info(f"Добавление нового чата: {update.chat.id}")
            self.db.add_chat(update.chat.id)
            await self.bot.send_message(
                update.chat.id,
                f"#NEWCHAT\n\nchatid: `{update.chat.id}`",
                parse_mode='markdown'
            )

    @staticmethod
    async def check_banned(user, message):
        if user and user[4] == 1:
            await message.reply('🛑 Вы заблокированы в боте!')
            return True
        return False

    async def profile_command(self, message: types.Message):
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
        user = self.db.get_user(user_id)
        if not user:
            await message.reply('❌ Профиль не найден')
            return

        username = f"@{user[5]}" if user[5] else "не указан"
        clan_name = self.db.get_clan_name(user[7]) if user[7] else "не в клане"
        status = "👑 Администратор" if user[3] else "Пользователь"

        profile_info = (f"{status}\n👤 Имя: {user[6]}\n"
                        f"👥 Клан: {clan_name}\n"
                        f"👥 Username: {username}\n"
                        f"🆔 ID: {user_id}\n"
                        f"🌿 Снюхано: {user[1]} грамм.")
        await message.reply(profile_info, parse_mode='markdown')

    async def drug_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user:
            self.db.create_user(user_id)
            user = self.db.get_user(user_id)

        if await self.check_banned(user, message):
            return

        current_time = datetime.now()
        drug_usage_timeout = timedelta(hours=1)
        minimum_drug_find_chance = 20
        drug_amount_range = (1, 10)

        last_use_time = datetime.fromisoformat(user[2]) if user[2] else None
        drug_count = user[1]

        if last_use_time and (current_time - last_use_time) < drug_usage_timeout:
            next_available_time = (current_time + drug_usage_timeout).strftime("%H:%M")
            await message.reply(
                f"❌ {message.from_user.first_name}, ты уже нюхал(-а)!\n\n"
                f"🌿 Всего снюхано `{drug_count} грамм` мефедрона\n\n"
                f"⏳ Приходи в {next_available_time}.",
                parse_mode='markdown')
        elif random.randint(0, 100) < minimum_drug_find_chance:
            await message.reply(f"🧂 {message.from_user.first_name}, ты просыпал(-а) весь мефчик!",
                                parse_mode='markdown')
            self.db.update_last_use_time(user_id, current_time.isoformat())
        else:
            next_available_time = (current_time + drug_usage_timeout).strftime("%H:%M")
            drug_count_to_add = random.randint(*drug_amount_range)
            self.db.update_drug_count(user_id, drug_count_to_add)
            await message.reply(
                f"👍 {message.from_user.first_name}, ты занюхнул(-а) {drug_count_to_add} грамм мефчика!\n\n"
                f"🌿 Всего снюхано `{drug_count + drug_count_to_add}` грамм мефедрона\n\n"
                f"⏳ Приходи в {next_available_time}.",
                parse_mode='markdown')

    async def top_command(self, message: types.Message):
        top_users = self.db.get_top_users()
        if not top_users:
            await message.reply('Никто еще не принимал меф.')
            return

        response = "🔝ТОП ЛЮТЫХ МЕФЕНДРОНЩИКОВ В МИРЕ🔝:\n"
        for rank, (user_id, drug_count) in enumerate(top_users, start=1):
            if user_id == self.bot.id:
                continue
            user_info = await self.bot.get_chat(user_id)
            response += f"{rank}) {user_info.full_name}: {drug_count} гр. мефа\n"
        await message.reply(response, parse_mode='markdown')

    async def take_command(self, message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        reply_msg = message.reply_to_message
        if not reply_msg:
            await message.reply('❌ Ответьте на сообщение пользователя, у которого хотите спиздить мефедрон.')
            return
        if reply_msg.from_user.id in [self.bot.id, message.from_user.id]:
            await message.reply(f'❌ Вы не можете забрать меф у бота или у себя')
            return

        target_user = self.db.get_user(reply_msg.from_user.id)
        if not target_user or not user:
            await message.reply('❌ Этот пользователь еще не нюхал меф или профиль не найден')
            return

        last_time = await state.get_data() or {'time': datetime.min}
        if datetime.now() - last_time['time'] < timedelta(days=1):
            await message.reply("❌ Нельзя пиздить меф так часто! Ты сможешь спиздить меф через 1 день.")
            return

        result = self.steal_drug(user, target_user)
        await message.reply(result, parse_mode='markdown')
        await state.set_data({'time': datetime.now()})

    def steal_drug(self, user, target_user):
        if target_user[1] < 1:
            return '❌ У жертвы недостаточно снюханного мефа для того чтобы его спиздить'
        if user[1] < 1:
            return '❌ У тебя недостаточно снюханного мефа для того пойти искать жертву'

        randomed = random.choice(['noticed', 'hit', 'pass'])
        if randomed == 'noticed':
            self.db.update_drug_count(user[0], -1)
            return '❌ *Жертва тебя заметила*, и ты решил убежать. Спиздить меф не получилось. Пока ты бежал, ' \
                   '*ты потерял* `1 гр.`'
        elif randomed == 'hit':
            self.db.update_drug_count(user[0], -1)
            return '❌ *Жертва тебя заметила*, и пизданула тебя бутылкой по башке бля. Спиздить меф не получилось. ' \
                   '*Жертва достала из твоего кармана* `1 гр.`'

        self.db.update_drug_count(target_user[0], -1)
        self.db.update_drug_count(user[0], -1)
        username_mention = f"[{target_user['username']}](tg://user?id={target_user['id']})" if target_user[
            'username'] else target_user['full_name']
        return f"✅ {user['full_name']} _спиздил(-а) один грам мефа у_ {username_mention}!"

    async def casino(self, message: types.Message):
        args = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        if len(args) < 2:
            await message.reply("🛑 Укажи сумму, на которую ты бы хотел сыграть! Пример:\n`/casino 40`",
                                parse_mode='markdown')
            return

        bet = int(args[1]) if args[1].isdigit() and int(args[1]) > 0 else None
        if bet is None:
            await message.reply("🛑 Нужно указать целое число больше нуля для ставки!", parse_mode='markdown')
            return

        last_used = user[5]
        if last_used and (datetime.now() - datetime.fromisoformat(last_used)).total_seconds() < 30:
            await message.reply('⏳ Ты только что *крутил казик*, солевая обезьяна, *подожди 30 секунд по братски.*',
                                parse_mode='markdown')
            return

        multipliers = [2, 1.5, 1.25, 1.1, 0]
        weights = [1, 2, 3, 4, 90]
        multiplier = random.choices(multipliers, weights=weights)[0]
        win_amount = round(bet * multiplier, 1) if multiplier else 0

        if multiplier:
            await message.reply(
                f'🤑 *Ебать тебе повезло!* Твоя ставка *умножилась* на `{multiplier}`. Твой выигрыш: `{win_amount}` гр.',
                parse_mode='markdown')
        else:
            await message.reply('😔 *Ты проебал* свою ставку, *нехуй было* крутить казик.', parse_mode='markdown')

        self.db.update_user(user_id, drug_count=user[1] + win_amount - bet, last_casino=datetime.now().isoformat())

    async def give_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply('❌ Необходимо указать количество граммов для передачи')
            return

        value = int(args[1]) if args[1].isdigit() and int(args[1]) > 0 else None
        if value is None:
            await message.reply('❌ Значение должно быть положительным числом и не равным нулю')
            return

        reply_msg = message.reply_to_message
        if not reply_msg or reply_msg.from_user.id in [user_id, self.bot.id]:
            await message.reply('❌ Некорректный получатель')
            return

        recipient_id = reply_msg.from_user.id
        recipient = self.db.get_user(recipient_id)

        if not recipient:
            await message.reply('❌ Профиль получателя не найден!')
            return

        if user[1] < value:
            await message.reply(f'❌ Недостаточно граммов мефа для передачи')
            return

        commission = round(value * 0.10)
        net_value = value - commission

        self.db.update_user(recipient_id, drug_count=recipient[1] + net_value)
        self.db.update_user(user_id, drug_count=user[1] - value)
        self.db.update_user(self.bot.id, drug_count=self.db.get_user(self.bot.id)[1] + commission)

        await message.reply(
            f"✅ {message.from_user.first_name}, ты передал(-а) {value} гр. мефа "
            f"пользователю {reply_msg.from_user.full_name}.\n"
            f"Комиссия: `{commission}` гр. мефа\nПолучено `{net_value}` гр. мефа.",
            parse_mode='markdown'
        )

    async def create_clan(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("🛑 Укажите название клана. Пример: `/clancreate КланНазвание`", parse_mode='markdown')
            return

        clan_name = args[1]
        clanexist = self.db.get_clan_by_name(clan_name)
        if clanexist:
            await message.reply('🛑 Клан с таким названием уже существует.')
            return

        if user[7]:
            await message.reply('🛑 Вы уже состоите в клане.')
            return

        if user[1] < 100:
            await message.reply("🛑 Недостаточно средств для создания клана. Необходимо минимум `100` гр.")
            return

        clan_id = random.randint(100000, 999999)
        self.db.create_clan(clan_id, clan_name, user_id, 0)
        self.db.update_user(user_id, clan_member=clan_id, drug_count=user[1] - 100)
        await message.reply(
            f"✅ Клан `{clan_name}` успешно создан. Ваш идентификатор клана: `{clan_id}`. С вашего баланса списано "
            f"`100` гр.",
            parse_mode='markdown')
        await self.bot.send_message(
            message.chat.id,
            f"#NEWCLAN\n\nclanid: `{clan_id}`\nclanname: `{clan_name}`\n"
            f"clanownerid: `{user_id}`",
            parse_mode='markdown'
        )

    async def deposit(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("🛑 Вы не указали сумму. Пример: `/deposit 100`", parse_mode='markdown')
            return

        cost = int(args[1]) if args[1].isdigit() else None
        if not cost or cost <= 0:
            await message.reply("❌ Введи целое число больше нуля.", parse_mode='markdown')
            return

        if user[7] == 0:
            await message.reply("🛑 Вы не состоите в клане", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(user[7])
        if not clan:
            await message.reply("🛑 Информация о клане не найдена", parse_mode='markdown')
            return

        if cost > user[1]:
            await message.reply(f"🛑 Недостаточно средств. Ваш баланс: `{user[1]}` гр.", parse_mode='markdown')
            return

        clan_balance = clan[3] + cost
        self.db.update_clan_balance_by_owner(clan[2], clan_balance)  # clan_owner_id
        self.db.update_user(user_id, drug_count=user[1] - cost)
        await message.reply(f"✅ Вы успешно пополнили баланс клана `{clan[1]}` на `{cost}` гр.",
                            parse_mode='markdown')  # clan_name
        await self.bot.send_message(
            message.chat.id,
            f"#DEPOSIT\n\nclanname: `{clan[1]}`\namount: `{cost}`\n"
            f"userid: `{user_id}`\nfirstname: {message.from_user.first_name}\n\n"
            f"[mention](tg://user?id={user_id})",
            parse_mode='markdown'
        )

    async def withdraw(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("🛑 Вы не указали сумму. Пример: `/withdraw 100`", parse_mode='markdown')
            return

        cost = int(args[1]) if args[1].isdigit() else None
        if not cost or cost <= 0:
            await message.reply("❌ Введи целое число больше нуля.", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(user[7])
        if not clan or user_id != clan[2]:
            await message.reply("🛑 Вы не являетесь владельцем клана или клан не найден.", parse_mode='markdown')
            return

        if cost > clan[3]:
            await message.reply(f"🛑 Недостаточно средств. Баланс клана: `{clan[3]}` гр.", parse_mode='markdown')
            return

        clan_balance = clan[3] - cost
        self.db.update_clan_balance_by_owner(user_id, clan_balance)
        self.db.update_user(user_id, drug_count=user[1] + cost)
        await message.reply(f"✅ Вы успешно сняли `{cost}` гр. мефа с баланса клана `{clan[1]}`",
                            parse_mode='markdown')  # clan_name
        await self.bot.send_message(
            message.chat.id,
            f"#WITHDRAW\n\namount: `{cost}`\nclanname: `{clan[1]}`\n"
            f"userid: {user_id}\n\n[mention](tg://user?id={user_id})",
            parse_mode='markdown'
        )

    async def clan_top(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        if await self.check_banned(user, message):
            return
        top_clans = self.db.get_top_clans()
        if top_clans:
            response = "🔝ТОП 10 МЕФЕДРОНОВЫХ КАРТЕЛЕЙ В МИРЕ🔝:\n" + "\n".join(
                f"{index}) *{clan[0]}*  `{clan[1]} гр. мефа`"
                for index, clan in enumerate(top_clans, start=1)
            )
            await message.reply(response, parse_mode='markdown')
        else:
            await message.reply('🛑 Ещё ни один клан не пополнил свой баланс.')

    async def clanbalance(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return
        clan_id = user[7]
        if not clan_id:
            await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            return
        clan_balance = self.db.get_clan_balance(clan_id)
        clan_name = self.db.get_clan_name(clan_id)
        await message.reply(f'✅ Баланс клана *{clan_name}* - `{clan_balance}` гр.', parse_mode='markdown')

    async def clanwar(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        clan_id = user[7]
        if not clan_id:
            await message.reply(f"🛑 *Вы не состоите в клане*", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(clan_id)
        clan_name = clan[1]
        if user_id != clan[2]:
            await message.reply(f"🛑 *Вы не являетесь владельцем клана*", parse_mode='markdown')
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply(f"🛑 *Вы не указали идентификатор клана для начала войны*", parse_mode='markdown')
            return
        target_clan_id = args[1]

        target_clan = self.db.get_clan_by_id(target_clan_id)
        if not target_clan:
            await message.reply(f"🛑 *Не удалось найти клан с указанным идентификатором*", parse_mode='markdown')
            return
        target_clan_name = target_clan[1]
        await message.reply(f"*Клан {clan_name} начал войну с {target_clan_name}!*", parse_mode='markdown')

        chats = self.db.get_all_chats()
        for chat_id in chats:
            try:
                await self.bot.send_message(chat_id[0],
                                            f"*Клан {clan_name} начал войну с {target_clan_name}!*",
                                            parse_mode='markdown')
            except Exception as e:
                print(f"Ошибка отправки сообщения в {chat_id}: {e}")

    async def clan_owner(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return

        clan_id = user[7]
        if not clan_id:
            await message.reply(f"🛑 *Вы не состоите в клане*", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(clan_id)
        if user_id != clan[2]:
            await message.reply(f"🛑 *Вы не являетесь владельцем клана*", parse_mode='markdown')
            return
        if message.reply_to_message:
            new_owner_id = message.reply_to_message.from_user.id
        elif len(message.text.split()) >= 2:
            new_owner_id = int(message.text.split()[1])
        else:
            await message.reply(f"🛑 *Вы не указали нового владельца клана*", parse_mode='markdown')
            return
        new_owner = self.db.get_user(new_owner_id)
        if not new_owner:
            await message.reply(f"🛑 *Не удалось найти пользователя с указанным идентификатором*",
                                parse_mode='markdown')
            return
        self.db.update_clan_owner(clan_id, new_owner_id)
        await message.reply(f"✅ *Вы передали владельца клана!*", parse_mode='markdown')

    async def claninfo(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        if await self.check_banned(user, message):
            return

        clan_id = user[7]
        if not clan_id:
            await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(clan_id)
        clan_balance = clan[3]
        clan_name = clan[1]
        clan_owner_id = clan[2]
        clan_owner = await self.bot.get_chat(clan_owner_id)
        await message.reply(
            f"👥 Клан: `{clan_name}`\n"
            f"👑 Владелец клана: [{clan_owner.first_name}](tg://user?id={clan_owner_id})\n"
            f"🌿 Баланс клана `{clan_balance}` гр.",
            parse_mode='markdown'
        )

    async def clanmembers(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user or await self.check_banned(user, message) or not user[7]:
            await message.reply(f"🛑 Вы не состоите в клане или заблокированы", parse_mode='markdown')
            return

        clan_members = self.db.get_clan_members(user[7])
        if not clan_members:
            await message.reply(f"🛑 В клане нет участников", parse_mode='markdown')
            return

        clan_name = self.db.get_clan_by_id(user[7])[1]
        response = f"👥 Список участников клана *{clan_name}*:\n"
        for counter, member in enumerate(clan_members, 1):
            member_info = await self.bot.get_chat(member[0])
            member_role = "👑" if member[0] == user[7] else ""
            response += f"{counter}) *{member_info.full_name}* {member_role}\n"
        await message.reply(response, parse_mode='markdown')

    async def claninvite(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        clan_id = user[7] if user else None
        if await self.check_banned(user, message) or not clan_id:
            return

        clan = self.db.get_clan_by_id(clan_id)
        if user_id != clan[2]:
            await message.reply(f"🛑 Только владелец клана может приглашать участников", parse_mode='markdown')
            return

        reply_msg = message.reply_to_message
        if not reply_msg:
            await message.reply(f"🛑 Ответьте на сообщение пользователя, которого хотите пригласить",
                                parse_mode='markdown')
            return

        if reply_msg.from_user.id == self.bot.id:
            await message.reply(f'❌ Бот не может быть приглашен в клан', parse_mode='markdown')
            return

        invited_user_id = reply_msg.from_user.id
        invited_user = self.db.get_user(invited_user_id)
        if invited_user[7]:
            await message.reply(f"🛑 Пользователь уже состоит в клане", parse_mode='markdown')
            return

        if invited_user[8]:
            await message.reply(f"🛑 У пользователя уже есть приглашение", parse_mode='markdown')
            return

        self.db.update_user_clan_invite(invited_user_id, clan_id)
        await message.reply(
            f'✅ Пользователь {reply_msg.from_user.first_name} приглашен в клан {clan[1]}',
            parse_mode='markdown'
        )

    async def clankick(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        clan_id = user[7] if user else None
        if await self.check_banned(user, message) or not clan_id:
            return

        clan = self.db.get_clan_by_id(clan_id)
        if user_id != clan[2]:
            await message.reply(f"🛑 Только владелец клана может исключать участников", parse_mode='markdown')
            return

        reply_msg = message.reply_to_message
        if not reply_msg:
            await message.reply(f"🛑 Ответьте на сообщение пользователя, которого хотите исключить",
                                parse_mode='markdown')
            return

        kicked_user_id = reply_msg.from_user.id
        self.db.remove_user_from_clan(kicked_user_id)
        await message.reply(
            f'✅ Пользователь {reply_msg.from_user.first_name} исключен из клана {clan[1]}',
            parse_mode='markdown'
        )

    async def clanleave(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        clan_id = user[7] if user else None
        if await self.check_banned(user, message) or not clan_id:
            return
        clan = self.db.get_clan_by_id(clan_id)
        if user_id == clan[2]:
            await message.reply(f"🛑 Владелец клана не может его покинуть", parse_mode='markdown')
            return

        self.db.remove_user_from_clan(user_id)
        await message.reply(f'✅ Вы покинули клан {clan[1]}', parse_mode='markdown')

    async def clandisband(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        clan_id = user[7] if user else None
        if await self.check_banned(user, message) or not clan_id:
            return
        clan = self.db.get_clan_by_id(clan_id)
        if user_id != clan[2]:
            await message.reply(f"🛑 Только владелец клана может его распустить", parse_mode='markdown')
            return

        self.db.delete_clan(clan_id)
        await message.reply(f'✅ Клан {clan[1]} распущен', parse_mode='markdown')

    async def clanaccept(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return
        if user[8]:
            self.db.update_user(user_id, clan_member=user[8], clan_invite=None)
            clan_name = self.db.get_clan_by_id(user[8])[1]
            await message.reply(f'✅ Вы приняли приглашение в клан {clan_name}', parse_mode='markdown')
        else:
            await message.reply('🛑 У вас нет приглашений', parse_mode='markdown')

    async def clandecline(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if await self.check_banned(user, message):
            return
        if user[8]:
            clan_name = self.db.get_clan_by_id(user[8])[1]
            self.db.update_user(user_id, clan_invite=None)
            await message.reply(f'❌ Вы отклонили приглашение в клан {clan_name}', parse_mode='markdown')
        else:
            await message.reply('🛑 У вас нет приглашений', parse_mode='markdown')

    async def drug_find(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        user_id = message.from_user.id
        if await self.check_banned(user, message):
            return
        drug_count = user[1] if user else 0
        last_find_time = user[6] if user and user[6] else datetime.min.isoformat()

        if (datetime.now() - datetime.fromisoformat(last_find_time)).total_seconds() < 43200:
            await message.reply('⏳ Ты недавно *ходил за кладом, подожди 12 часов.*', parse_mode='markdown')
            return
        else:
            if random.randint(1, 100) > 50:
                count = random.randint(1, 10)
                if user:
                    self.db.update_user(user_id, drug_count=drug_count + count)
                else:
                    self.db.add_user(user_id, drug_count=count)
                self.db.update_user(user_id, last_use_time='2006-02-20 12:45:37.666666',
                                    last_find=datetime.now().isoformat())
                await self.bot.send_message(
                    message.chat.id,
                    f"#FIND #WIN\n\nfirst\\_name: `{message.from_user.first_name}`\n"
                    f"count: `{count}`\ndrug\\_count: `{drug_count + count}`\n\n"
                    f"[mention](tg://user?id={user_id})",
                    parse_mode='markdown'
                )
                await message.reply(
                    f"👍 {message.from_user.first_name}, ты пошёл в лес и *нашел клад*, там лежало `{count} гр.` "
                    f"мефчика!\n🌿 Твое время команды /drug обновлено",
                    parse_mode='markdown')
            elif random.randint(1, 100) <= 50:
                count = random.randint(1, round(drug_count))
                self.db.update_user(user_id, drug_count=drug_count - count)
                await self.bot.send_message(
                    message.chat.id,
                    f"#FIND #LOSE\n\nfirst\\_name: `{message.from_user.first_name}`\n"
                    f"count: `{count}`\ndrug\\_count: `{drug_count - count}`\n\n"
                    f"[mention](tg://user?id={user_id})",
                    parse_mode='markdown'
                )
                await message.reply(
                    f"❌ *{message.from_user.first_name}*, тебя *спалил мент* и *дал тебе по ебалу*\n🌿 Тебе нужно "
                    f"откупиться, мент предложил взятку в размере `{count} гр.`\n⏳ Следующая попытка доступна через "
                    f"*12 часов.*",
                    parse_mode='markdown')

    async def banuser_command(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        if user and user[3]:
            ban_user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
            if ban_user_id:
                self.db.update_user(ban_user_id, is_banned=1)
                await message.reply(f"🛑 Пользователь с ID: `{ban_user_id}` заблокирован", parse_mode='markdown')
            else:
                await message.reply('Не указан ID пользователя для блокировки.')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def unbanuser_command(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        if user and user[3]:
            ban_user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
            if ban_user_id:
                self.db.update_user(ban_user_id, is_banned=0)
                await message.reply(f"🛑 Пользователь с ID: `{ban_user_id}` заблокирован", parse_mode='markdown')
            else:
                await message.reply('Не указан ID пользователя для блокировки.')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def setdrugs_command(self, message: types.Message):
        admin_user = self.db.get_user(message.from_user.id)
        if not admin_user or admin_user[3] != 1:
            await message.reply('🚨 Вы не имеете права использовать эту команду.')
            return

        reply_msg = message.reply_to_message
        if not reply_msg:
            await message.reply('🚨 Ответьте на сообщение пользователя, чтобы установить количество грамм.')
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply('🚨 Ошибка: нужно указать количество грамм.')
            return

        try:
            drug_amount = int(args[1])
            target_user_id = reply_msg.from_user.id
            self.db.update_user(target_user_id, drug_count=drug_amount)
            await message.reply(
                f'✅ Количество грамм для пользователя {reply_msg.from_user.full_name} обновлено до {drug_amount}.')
        except ValueError:
            await message.reply('🚨 Ошибка: количество грамм должно быть целым числом.')

    async def usercount(self, message: types.Message):
        user = self.db.get_user(message.from_user.id)
        if user and user[3]:
            user_count = len(self.db.get_top_users(limit=None))
            await message.reply(f'Количество пользователей в боте: {user_count}')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def cmd_broadcast_start(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if not user or user[3] != 1:
            await message.reply('🚨 MONKEY ALARM')
            return

        reply = message.reply_to_message
        if not reply:
            await message.reply('Ответь на сообщение с текстом или фото для рассылки')
            return

        all_chats = self.db.get_all_chats()
        await message.reply('Начинаю рассылку')
        for chat_id in all_chats:
            try:
                if reply.photo:
                    photo_id = reply.photo[-1].file_id
                    caption = reply.caption if reply.caption else ''
                    await self.bot.send_photo(chat_id, photo_id, caption=caption, parse_mode='markdown')
                else:
                    await self.bot.send_message(chat_id, reply.text, parse_mode='markdown')
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения в {chat_id}: {e}")
