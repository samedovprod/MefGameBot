import random
import sys
from datetime import datetime, timedelta

from aiogram import types
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatMemberUpdated


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
        await message.reply('''Правила пользования MefMetrBot:
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
        if update.new_chat_member.user.id == self.bot.id and update.new_chat_member.status == 'member':
            self.db.add_chat(update.chat.id)
            await self.bot.send_message(
                update.chat.id,
                f"#NEWCHAT\n\nchatid: `{update.chat.id}`",
                parse_mode='markdown'
            )

        # @dp.message_handler(commands=['casino'])
        # async def start_command(message: types.Message):
        #     await message.reply("❌ *Резерв казино закончился. Попробуйте, пожалуйста, позже!*", parse_mode='markdown')

    @staticmethod
    async def check_banned(user, message):
        if user and user[4] == 1:
            await message.reply('🛑 Вы заблокированы в боте!')
            return True
        return False

    def get_user_info(self, message):
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = message.from_user.id
        return self.db.get_user(user_id)

    async def profile_command(self, message: types.Message):
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = message.from_user.id

        user = self.db.get_user(user_id)
        if not user:
            await message.reply('❌ Профиль не найден')
            return

        drug_count = user[1]
        is_admin = user[3]
        clan_member = user[7]
        clan_name = self.db.get_clan_by_name(clan_member) if clan_member else None

        if user_id == message.from_user.id:
            username = message.from_user.username.replace('_', '\_') if message.from_user.username else None
            full_name = message.from_user.full_name
        else:
            username = message.reply_to_message.from_user.username.replace('_',
                                                                           '\_') if message.reply_to_message.from_user.username else None
            full_name = message.reply_to_message.from_user.full_name

        if is_admin == 1:
            if clan_member:
                await message.reply(
                    f"👑 *Администратор*\n👤 *Имя:* _{full_name}_\n👥 *Клан:* *{clan_name}*\n👥 *Username "
                    f"пользователя:* @{username}\n🆔 *ID пользователя:* `{user_id}`\n🌿 *Снюхано* _{drug_count}_ "
                    f"грамм.",
                    parse_mode='markdown')
            else:
                await message.reply(
                    f"👑 *Администратор*\n👤 *Имя:* _{full_name}_\n👥 *Username пользователя:* @{username}\n🆔 "
                    f"*ID пользователя:* `{user_id}`\n🌿 *Снюхано* _{drug_count}_ грамм.",
                    parse_mode='markdown')
        else:
            if clan_member:
                await message.reply(
                    f"👤 *Имя:* _{full_name}_\n👥 *Клан:* *{clan_name}*\n👥 *Username пользователя:* @{username}\n🆔 *ID пользователя:* `{user_id}`\n🌿 *Снюхано* _{drug_count}_ грамм.",
                    parse_mode='markdown')
            else:
                await message.reply(
                    f"👤 *Имя:* _{full_name}_\n👥 *Username пользователя:* @{username}\n🆔 *ID пользователя: * `{user_id}`\n🌿 *Снюхано* _{drug_count}_ грамм.",
                    parse_mode='markdown')

    async def drug_command(self, message: types.Message, state: FSMContext):
        format = '%Y-%m-%d %H:%M:%S.%f'
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        drug_count = user[1] if user else 0
        last_use_time = user[2] if user else 0
        is_admin = user[3] if user else 0
        is_banned = user[4] if user else 0
        use_time = datetime.strptime(last_use_time, format) if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if last_use_time and (datetime.now() - use_time) < timedelta(hours=1):
                remaining_time = timedelta(hours=1) - (datetime.now() - use_time)
                await message.reply(
                    f"❌ *{message.from_user.first_name}*, _ты уже нюхал(-а)!_\n\n🌿 Всего снюхано `{drug_count} грамм` "
                    f"мефедрона\n\n⏳ Следующий занюх доступен через `1 час.`",
                    parse_mode='markdown')
            elif random.randint(0, 100) < 20:
                if last_use_time and (datetime.now() - use_time) < timedelta(hours=1):
                    remaining_time = timedelta(hours=1) - (datetime.now() - use_time)
                    await message.reply(
                        f"🧂 *{message.from_user.first_name}*, _ты просыпал(-а) весь мефчик!_\n\n🌿 Всего снюхано `{drug_count}` грамм мефедрона\n\n⏳ Следующий занюх доступен через `1 час.`",
                        parse_mode='markdown')
                    self.db.update_last_use_time(user_id, datetime.now())
            else:
                count = random.randint(1, 10)
                if user:
                    self.db.update_drug_count(user_id, count)
                else:
                    self.db.create_user(user_id, drug_count=count)
                self.db.update_last_use_time(user_id, datetime.now())
                await message.reply(
                    f"👍 *{message.from_user.first_name}*, _ты занюхнул(-а) {count} грамм мефчика!_\n\n🌿 Всего снюхано `{drug_count + count}` грамм мефедрона\n\n⏳ Следующий занюх доступен через `1 час.`",
                    parse_mode='markdown')

    async def top_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            top_users = self.db.get_top_users()
            if top_users:
                response = "🔝ТОП 10 ЛЮТЫХ МЕФЕНДРОНЩИКОВ В МИРЕ🔝:\n"
                counter = 1
                for user in top_users:
                    user_id = user[0]
                    if user_id == self.bot.id:
                        continue
                    drug_count = user[1]
                    user_info = await self.bot.get_chat(user_id)
                    response += f"{counter}) *{user_info.full_name}*: `{drug_count} гр. мефа`\n"
                    counter += 1
                await message.reply(response, parse_mode='markdown')
            else:
                await message.reply('Никто еще не принимал меф.')

    async def take_command(self, message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            reply_msg = message.reply_to_message
            if reply_msg and reply_msg.from_user.id == self.bot.id:
                await message.reply(f'❌ Вы не можете забрать меф у бота')
                return
            elif reply_msg and reply_msg.from_user.id != message.from_user.id:
                user_id = reply_msg.from_user.id
                user = self.db.get_user(user_id)
                your_user_id = message.from_user.id
                your_user = self.db.get_user(your_user_id)
                if user and your_user:
                    drug_count = user[1]
                    your_drug_count = your_user[1]
                    if drug_count > 1 and your_drug_count > 1:
                        last_time = await state.get_data()
                        if last_time and (datetime.now() - last_time['time']) < timedelta(days=1):
                            remaining_time = timedelta(days=1) - (datetime.now() - last_time['time'])
                            await message.reply(
                                f"❌ Нельзя пиздить меф так часто! Ты сможешь спиздить меф через 1 день.")
                        else:
                            variables = ['noticed', 'hit', 'pass']
                            randomed = random.choice(variables)
                            if randomed == 'noticed':
                                self.db.update_user(your_user_id, drug_count=-1)
                                await message.reply(
                                    '❌ *Жертва тебя заметила*, и ты решил убежать. Спиздить меф не получилось. Пока ты '
                                    'бежал, *ты потерял* `1 гр.`',
                                    parse_mode='markdown')
                            elif randomed == 'hit':
                                self.db.update_user(your_user_id, drug_count=-1)
                                await message.reply(
                                    '❌ *Жертва тебя заметила*, и пизданула тебя бутылкой по башке бля. Спиздить меф не '
                                    'получилось. *Жертва достала из твоего кармана* `1 гр.`',
                                    parse_mode='markdown')

                            elif randomed == 'pass':
                                self.db.update_user(user_id, drug_count=-1)
                                self.db.update_user(your_user_id, drug_count=1)
                                if reply_msg.from_user.username:
                                    username = reply_msg.from_user.username.replace('_', '\_')
                                else:
                                    username = f'[{reply_msg.from_user.first_name}](tg://user?id={reply_msg.from_user.id})'
                                await message.reply(
                                    f"✅ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) _спиздил("
                                    f"-а) один грам мефа у_ @{username}!",
                                    parse_mode='markdown')
                            await state.set_data({'time': datetime.now()})
                    elif drug_count < 1:
                        await message.reply('❌ У жертвы недостаточно снюханного мефа для того чтобы его спиздить')
                    elif your_drug_count < 1:
                        await message.reply('❌ У тебя недостаточно снюханного мефа для того пойти искать жертву')
                else:
                    await message.reply('❌ Этот пользователь еще не нюхал меф')
            else:
                await message.reply('❌ Ответьте на сообщение пользователя, у которого хотите спиздить мефедрон.')

    async def casino(self, message: types.Message):
        args = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user:
            await message.reply('🛑 Ваш профиль не найден.')
            return

        if user[4]:
            await message.reply('🛑 Вы заблокированы в боте.')
            return

        if len(args) < 2:
            await message.reply("🛑 Укажи сумму, на которую ты бы хотел сыграть! Пример:\n`/casino 40`",
                                parse_mode='markdown')
            return

        try:
            bet = int(args[1])
            if bet < 1:
                await message.reply("🛑 Ставка должна быть больше 0.", parse_mode='markdown')
                return
        except ValueError:
            await message.reply("🛑 Нужно указать целое число!", parse_mode='markdown')
            return

        drug_count = user[1]
        if bet > drug_count:
            await message.reply("🛑 Твоя ставка больше твоего баланса!", parse_mode='markdown')
            return

        last_used = user[5]
        if last_used and (datetime.now() - datetime.fromisoformat(last_used)).total_seconds() < 30:
            await message.reply('⏳ Ты только что *крутил казик*, солевая обезьяна, *подожди 30 секунд по братски.*',
                                parse_mode='markdown')
            return

        randomed = random.randint(1, 100)
        multipliers = [2, 1.5, 1.25, 1.1, 0]
        weights = [1, 2, 3, 4, 90]
        multiplier = random.choices(multipliers, weights=weights)[0]

        if multiplier:
            win_amount = round(bet * multiplier, 1)
            self.db.update_user(user_id, drug_count=drug_count + win_amount - bet)
            await message.reply(
                f'🤑 *Ебать тебе повезло!* Твоя ставка *умножилась* на `{multiplier}`. Твой выигрыш: `{win_amount}` гр.',
                parse_mode='markdown')
        else:
            self.db.update_user(user_id, drug_count=drug_count - bet)
            await message.reply('😔 *Ты проебал* свою ставку, *нехуй было* крутить казик.', parse_mode='markdown')

        self.db.update_user(user_id, last_casino=datetime.now().isoformat())

    async def give_command(self, message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        if not user or user[4]:
            await message.reply('🛑 Вы заблокированы в боте или профиль не найден!')
            return

        args = message.text.split(maxsplit=1)
        if not args:
            await message.reply('❌ Необходимо указать количество граммов для передачи')
            return

        try:
            value = int(args[0])
            if value <= 0:
                await message.reply(f'❌ Значение должно быть положительным числом')
                return
        except ValueError:
            await message.reply(f'❌ Введи целое число')
            return

        reply_msg = message.reply_to_message
        if not reply_msg or reply_msg.from_user.id == user_id or reply_msg.from_user.id == self.bot.id:
            await message.reply(f'❌ Некорректный получатель')
            return

        recipient_id = reply_msg.from_user.id
        recipient = self.db.get_user(recipient_id)
        if not recipient:
            await message.reply(f'❌ Профиль получателя не найден!')
            return

        your_drug_count = user[1]
        if your_drug_count < value:
            await message.reply(f'❌ Недостаточно граммов мефа для передачи')
            return

        commission = round(value * 0.10)
        net_value = value - commission
        botbalance = self.db.get_user(self.bot.id)[1]

        self.db.update_user(recipient_id, drug_count=net_value)
        self.db.update_user(user_id, drug_count=-value)
        self.db.update_user(self.bot.id, drug_count=botbalance + commission)

        await self.bot.send_message(message.chat.id,
                                    f"#GIVE\n\nfirst\_name: `{message.from_user.first_name}`\nuserid: `{user_id}`\nto: `{reply_msg.from_user.first_name}`\nvalue: `{net_value}`",
                                    parse_mode='markdown')

        if reply_msg.from_user.username:
            username_mention = f"[{reply_msg.from_user.first_name}](tg://user?id={recipient_id})"
        else:
            username_mention = reply_msg.from_user.first_name

        await message.reply(
            f"✅ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) подарил(-а) {value} гр. мефа {username_mention}!\n"
            f"Комиссия: `{commission}` гр. мефа\nПолучено `{net_value}` гр. мефа.",
            parse_mode='markdown')

        await state.set_data({'time': datetime.now()})

    async def create_clan(self, message: types.Message):
        args = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user:
            await message.reply('🛑 Ваш профиль не найден.')
            return

        if user[4]:
            await message.reply('🛑 Вы заблокированы в боте.')
            return

        if len(args) < 2:
            await message.reply("🛑 Укажите название клана. Пример: `/clancreate КланНазвание`",
                                parse_mode='markdown')
            return

        clan_name = args[1]
        clanexist = self.db.get_clan_by_name(clan_name)
        if clanexist:
            await message.reply('🛑 Клан с таким названием уже существует.')
            return

        if user[7]:
            await message.reply('🛑 Вы уже состоите в клане.')
            return

        drug_count = user[1] or 0
        if drug_count < 100:
            await message.reply("🛑 Недостаточно средств для создания клана. Необходимо минимум `100` гр.")
            return

        clan_id = random.randint(100000, 999999)
        self.db.create_clan(clan_id, clan_name, user_id, 0)
        self.db.update_user(user_id, clan_member=clan_id, drug_count=drug_count - 100)
        await self.bot.send_message(
            message.chat.id,
            f"#NEWCLAN\n\nclanid: `{clan_id}`\nclanname: `{clan_name}`\nclanownerid: `{user_id}`",
            parse_mode='markdown')
        await message.reply(
            f"✅ Клан `{clan_name}` успешно создан. Ваш идентификатор клана: `{clan_id}`. С вашего баланса списано `100` гр.",
            parse_mode='markdown')

    async def deposit(self, message: types.Message):
        args = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user or user[4]:
            await self.check_banned(user, message)
            return

        if len(args) < 2:
            await message.reply(f"🛑 Вы не указали сумму. Пример:\n`/deposit 100`", parse_mode='markdown')
            return

        try:
            cost = int(args[1])
            if cost <= 0:
                await message.reply(f'❌ Значение должно быть положительным числом и не равным нулю')
                return
        except ValueError:
            await message.reply(f'❌ Введи целое число')
            return

        user_balance = user[1]
        clan_id = user[7]

        if clan_id == 0:
            await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(clan_id)
        if not clan:
            await message.reply(f"🛑 Информация о клане не найдена", parse_mode='markdown')
            return

        clan_balance = clan[3]
        clan_name = clan[1]
        clan_owner_id = clan[2]

        if cost > user_balance:
            await message.reply(f"🛑 Недостаточно средств. Ваш баланс: `{user_balance}` гр.", parse_mode='markdown')
            return

        new_clan_balance = clan_balance + cost
        self.db.update_clan_balance_by_owner(clan_owner_id, new_clan_balance)
        self.db.update_user(user_id, drug_count=user_balance - cost)

        await message.reply(f"✅ Вы успешно пополнили баланс клана `{clan_name}` на `{cost}` гр.",
                            parse_mode='markdown')
        await self.bot.send_message(
            message.chat.id,
            f"#DEPOSIT\n\nclanname: `{clan_name}`\namount: `{cost}`\nuserid: `{user_id}`\nfirstname: {message.from_user.first_name}\n\n[mention](tg://user?id={user_id})",
            parse_mode='markdown'
        )

    async def withdraw(self, message: types.Message):
        args = message.text.split()
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if not user or user[4]:
            await self.check_banned(user, message)
            return

        if not args:
            await message.reply(f"🛑 Вы не указали сумму. Пример:\n`/withdraw 100`", parse_mode='markdown')
            return

        try:
            cost = int(args[0])
            if cost <= 0:
                await message.reply(f'❌ Значение должно быть положительным числом')
                return
        except ValueError:
            await message.reply(f'❌ Введи целое число')
            return

        clan_id = user[1]
        if clan_id == 0:
            await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            return

        clan = self.db.get_clan_by_id(clan_id)
        if not clan:
            await message.reply(f"🛑 Информация о клане не найдена", parse_mode='markdown')
            return

        clan_balance, clan_name, clan_owner_id = clan[3], clan[1], clan[2]
        if user_id != clan_owner_id:
            await message.reply(f"🛑 Снимать деньги со счёта клана может только его владелец.", parse_mode='markdown')
            return

        if cost > clan_balance:
            await message.reply(f"🛑 Недостаточно средств. Баланс клана: `{clan_balance}` гр.", parse_mode='markdown')
            return

        self.db.update_clan_balance_by_owner(user_id, clan_balance - cost)
        self.db.update_user(user_id, drug_count=user[0] + cost)

        await message.reply(
            f"✅ Вы успешно сняли `{cost}` гр. мефа с баланса клана `{clan_name}`",
            parse_mode='markdown')
        await self.bot.send_message(message.chat.id,
                                    f"#WITHDRAW\n\namount: `{cost}`\nclanname: `{clan_name}`\nuserid: {user_id}\n\n[mention](tg://user?id={user_id})",
                                    parse_mode='markdown')

    async def clan_top(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            top_clans = self.db.get_top_clans()
            if top_clans:
                response = "🔝ТОП 10 МЕФЕДРОНОВЫХ КАРТЕЛЕЙ В МИРЕ🔝:\n"
                counter = 1
                for clan in top_clans:
                    clan_name = clan[0]
                    clan_balance = clan[1]
                    response += f"{counter}) *{clan_name}*  `{clan_balance} гр. мефа`\n"
                    counter += 1
                await message.reply(response, parse_mode='markdown')
            else:
                await message.reply('🛑 Ещё ни один клан не пополнил свой баланс.')

    async def clanbalance(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            elif clan_id > 0:
                clan_balance = clan[3]
                clan_name = clan[1]
                await message.reply(f'✅ Баланс клана *{clan_name}* - `{clan_balance}` гр.', parse_mode='markdown')

    async def clanwar(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 *Вы не состоите в клане*", parse_mode='markdown')
            elif clan_id > 0:
                clan_name = clan[1]
                clan_owner_id = clan[2]
                if user_id != clan_owner_id:
                    await message.reply(f"🛑 *Вы не являетесь владельцем клана*", parse_mode='markdown')
                    return
                if len(message.text.split()) < 2:
                    await message.reply(f"🛑 *Вы не указали идентификатор клана для начала войны*",
                                        parse_mode='markdown')
                    return
                target_clan_id = message.text.split()[1]
                target_clan = self.db.get_clan_by_id(target_clan_id)
                if not target_clan:
                    await message.reply(f"🛑 *Не удалось найти клан с указанным идентификатором*",
                                        parse_mode='markdown')
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
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 *Вы не состоите в клане*", parse_mode='markdown')
            elif clan_id > 0:
                current_owner_id = clan[2]
                if user_id != current_owner_id:
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
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            elif clan_id > 0:
                clan_balance = clan[0]
                clan_name = clan[1]
                clan_owner_id = clan[2]
                clan_owner = await self.bot.get_chat(clan_owner_id)
                await message.reply(
                    f"👥 Клан: `{clan_name}`\n👑 Владелец клана: [{clan_owner.first_name}](tg://user?id={clan_owner_id})\n🌿 Баланс клана `{clan_balance}` гр.",
                    parse_mode='markdown')

    async def clanmembers(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0

        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            clan_id = user[7] if user else 0
            clan_members = self.db.get_clan_members(clan_id)
            clan = self.db.get_clan_by_id(clan_id)
            if clan:
                clan_name = clan[0]
                clan_owner_id = clan[1]
                if clan_id > 0:
                    if clan_members:
                        response = f"👥 Список участников клана *{clan_name}*:\n"
                        counter = 1
                        clan_owner = None
                        for member in clan_members:
                            if member[0] == clan_owner_id:
                                clan_owner = member
                                break
                        if clan_owner:
                            user_info = await self.bot.get_chat(clan_owner[0])
                            response += f"{counter}) *{user_info.full_name}* 👑\n"
                            counter += 1
                        for member in clan_members:
                            if member[0] != clan_owner_id:
                                user_info = await self.bot.get_chat(member[0])
                                response += f"{counter}) {user_info.full_name}\n"
                                counter += 1
                        await message.reply(response, parse_mode='markdown')
            else:
                await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')

    async def claninvite(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan:
                clan_name = clan[1]
                clan_owner_id = clan[2]
                if user_id == clan_owner_id:
                    reply_msg = message.reply_to_message
                    if reply_msg and reply_msg.from_user.id == self.bot.id:
                        await message.reply(f'❌ Вы не можете пригласить бота в клан')
                        return
                    elif reply_msg:
                        invited_user_id = reply_msg.from_user.id
                        invited_user = self.db.get_user(invited_user_id)
                        clan_member = invited_user[7]
                        clan_invite = invited_user[8]

                        if clan_member == 0 and clan_invite == 0:
                            self.db.update_user(invited_user_id, clan_invite=clan_id)
                            await message.reply(
                                f'✅ Пользователь {reply_msg.from_user.first_name} *приглашён в клан {clan_name}* '
                                f'пользователем {message.from_user.first_name}\nДля того чтобы принять приглашение, '
                                f'*введите команду* `/clanaccept`\nДля того чтобы отказаться от приглашения, '
                                f'*введите команду* `/clandecline`',
                                parse_mode='markdown')
                        elif clan_invite > 0:
                            await message.reply(f"🛑 Этот пользователь уже имеет активное приглашение",
                                                parse_mode='markdown')
                        elif clan_member > 0:
                            await message.reply(f"🛑 Этот пользователь уже в клане", parse_mode='markdown')
                else:
                    await message.reply(f"🛑 Приглашать в клан может только создатель", parse_mode='markdown')
            else:
                await message.reply(f"🛑 {sys.exc_info()[0]}")

    async def clankick(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        clan_name = clan[1]
        clan_owner_id = int(clan[2])
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            elif clan_id > 0 and user_id == clan_owner_id:
                reply_msg = message.reply_to_message
                if reply_msg:
                    kicked_user_id = reply_msg.from_user.id
                    self.db.update_user(kicked_user_id, clan_member=0)
                    await message.reply(
                        f'✅ Пользователь @{reply_msg.from_user.username} *исключен из клана {clan_name}* пользователем @{message.from_user.username}',
                        parse_mode='markdown')
            else:
                await message.reply(f"🛑 Исключать из клана может только создатель", parse_mode='markdown')

    async def clanleave(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        clan_name = clan[1]
        clan_owner_id = int(clan[2])
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id == 0:
                await message.reply(f"🛑 Вы не состоите в клане", parse_mode='markdown')
            elif clan_id > 0 and user_id != clan_owner_id:
                self.db.update_user(user_id, clan_member=0)
                await message.reply(f'✅ *Вы покинули* клан *{clan_name}*', parse_mode='markdown')
            elif clan_id > 0 and user_id == clan_owner_id:
                await message.reply(f"🛑 Создатель клана не может его покинуть", parse_mode='markdown')

    async def clandisband(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_id = user[7] if user else 0
        clan = self.db.get_clan_by_id(clan_id)
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_id > 0 and user_id == clan[2]:
                self.db.delete_clan(clan_id)
                self.db.update_users_with_clan_id(clan_id, clan_member=0, clan_invite=0)
                await message.reply(f'✅ Вы распустили клан `{clan[1]}`', parse_mode='markdown')
            else:
                await message.reply(f"🛑 Вы не владелец клана!", parse_mode='markdown')

    async def clanaccept(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_invite = user[8] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_invite:
                clan = self.db.get_clan_by_id(clan_invite)
                self.db.update_user(user_id, clan_member=clan_invite, clan_invite=0)
                await message.reply(f'✅ *Вы приняли* приглашение в клан *{clan[1]}*', parse_mode='markdown')
            else:
                await message.reply('🛑 Вы ещё не получали приглашений в клан')

    async def clandecline(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_banned = user[4] if user else 0
        clan_invite = user[8] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if clan_invite:
                clan = self.db.get_clan_by_id(clan_invite)
                self.db.update_user(user_id, clan_invite=0)
                await message.reply(f'❌ *Вы отклонили* приглашение в клан *{clan[1]}*', parse_mode='markdown')
            else:
                await message.reply('🛑 Вы ещё не получали приглашений в клан')

    async def drug_find(self, message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        drug_count = user[1] if user else 0
        last_time = await state.get_data()
        last_used = user[6] if user else '2021-02-14 16:04:04.465506'
        is_banned = user[4] if user else 0
        if await self.check_banned(user, message):
            return
        elif is_banned == 0:
            if last_used is not None and (
                    datetime.now() - datetime.fromisoformat(last_used)).total_seconds() < 43200:
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
                    await self.bot.send_message(message.chat.id,
                                                f"#FIND #WIN\n\nfirst\_name: `{message.from_user.first_name}`\ncount: `{count}`\ndrug\_count: `{drug_count + count}`\n\n[mention](tg://user?id={user_id})",
                                                parse_mode='markdown')
                    await message.reply(
                        f"👍 {message.from_user.first_name}, ты пошёл в лес и *нашел клад*, там лежало `{count} гр.` "
                        f"мефчика!\n🌿 Твое время команды /drug обновлено",
                        parse_mode='markdown')
                elif random.randint(1, 100) <= 50:
                    count = random.randint(1, round(drug_count))
                    self.db.update_user(user_id, drug_count=drug_count - count)
                    await self.bot.send_message(message.chat.id,
                                                f"#FIND #LOSE\n\nfirst\_name: `{message.from_user.first_name}`\ncount: `{count}`\ndrug\_count: `{drug_count - count}`\n\n[mention](tg://user?id={user_id})",
                                                parse_mode='markdown')
                    await message.reply(
                        f"❌ *{message.from_user.first_name}*, тебя *спалил мент* и *дал тебе по ебалу*\n🌿 Тебе нужно "
                        f"откупиться, мент предложил взятку в размере `{count} гр.`\n⏳ Следующая попытка доступна через "
                        f"*12 часов.*",
                        parse_mode='markdown')

    async def banuser_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_admin = user[3]
        if is_admin == 1:
            bann_user_id = None
            reply_msg = message.reply_to_message
            if reply_msg and reply_msg.from_user.id != user_id:
                bann_user_id = reply_msg.from_user.id
            else:
                args = message.text.split()
                if len(args) > 1:
                    try:
                        bann_user_id = int(args[1])
                    except ValueError:
                        await message.reply('Некорректный ID пользователя.')
                        return

            if bann_user_id:
                self.db.update_user(bann_user_id, is_banned=1)
                await message.reply(f"🛑 Пользователь с ID: `{bann_user_id}` заблокирован", parse_mode='markdown')
                await self.bot.send_message(message.chat.id, f"#BAN\n\nid: {bann_user_id}")
            else:
                await message.reply('Не указан ID пользователя.')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def unbanuser_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_admin = user[3]
        if is_admin == 1:
            bann_user_id = None
            reply_msg = message.reply_to_message
            if reply_msg and reply_msg.from_user.id != user_id:
                bann_user_id = reply_msg.from_user.id
            else:
                args = message.text.split()
                if len(args) > 1:
                    try:
                        bann_user_id = int(args[1])
                    except ValueError:
                        await message.reply('Некорректный ID пользователя.')
                        return

            if bann_user_id:
                self.db.update_user(bann_user_id, is_banned=0)
                await message.reply(f"🛑 Пользователь с ID: `{bann_user_id}` разблокирован", parse_mode='markdown')
                await self.bot.send_message(message.chat.id, f"#UNBAN\n\nid: {bann_user_id}")
            else:
                await message.reply('Не указан ID пользователя.')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def setdrugs_command(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)

        if user[3] != 1:
            await message.reply('🚨 MONKEY ALARM')
            return

        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply(
                '🚨 Неправильное использование команды. Нужно указать ID пользователя и количество грамм.')
            return

        target_user_id, drug_amount = args[1], args[2]
        try:
            target_user_id = int(target_user_id)
            drug_amount = int(drug_amount)
        except ValueError:
            await message.reply('🚨 Ошибка: нужно ввести целые числа для ID пользователя и количества грамм.')
            return

        self.db.update_user(target_user_id, drug_count=drug_amount)
        await message.reply('✅ Количество грамм обновлено.')

    async def usercount(self, message: types.Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_admin = user[3]
        user_count = len(self.db.get_top_users(limit=None))
        if is_admin == 1:
            await message.reply(f'Количество пользователей в боте: {user_count}')
        else:
            await message.reply('🚨 MONKEY ALARM')

    async def cmd_broadcast_start(self, message: Message):
        user_id = message.from_user.id
        user = self.db.get_user(user_id)
        is_admin = user[3]
        all_chats = self.db.get_all_chats()
        reply = message.reply_to_message
        if is_admin == 1:
            if reply:
                if reply.photo:
                    if reply.caption:
                        await message.reply('Начинаю рассылку')
                        for chat_id in all_chats:
                            try:
                                await self.bot.send_photo(chat_id, reply.photo[-1].file_id,
                                                          caption=f"{reply.caption}",
                                                          parse_mode='markdown')
                            except:
                                await self.bot.send_message(message.chat.id,
                                                            f"#SENDERROR\n\nchatid: {chat_id}\nerror: {sys.exc_info()[0]}")
                                continue
                    else:
                        await message.reply('Начинаю рассылку')
                        for chat_id in all_chats:
                            try:
                                await self.bot.send_photo(chat_id, reply.photo[-1].file_id)
                            except:
                                await self.bot.send_message(message.chat.id,
                                                            f"#SENDERROR\n\nchatid: {chat_id}\nerror: {sys.exc_info()[0]}")
                                continue
                elif reply.text:
                    await message.reply('Начинаю рассылку')
                    for chat_id in all_chats:
                        try:
                            await self.bot.send_message(chat_id, f"{reply.text}", parse_mode='markdown')
                        except:
                            await self.bot.send_message(message.chat.id,
                                                        f"#SENDERROR\n\nchatid: {chat_id}\nerror: {sys.exc_info()[0]}")
                            continue
            else:
                await message.reply('Ответь на сообщение с текстом или фото для рассылки')
        else:
            await message.reply('🚨 MONKEY ALARM')
