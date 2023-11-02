import sqlite3


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, drug_count INTEGER, last_use_time TEXT,'
            'is_admin INTEGER, is_banned INTEGER, last_casino TEXT, last_find TEXT, clan_member INTEGER, '
            'clan_invite INTEGER, first_name TEXT)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS chats (chat_id INTEGER PRIMARY KEY, is_ads_enable INTEGER DEFAULT 1)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS clans (clan_id INTEGER PRIMARY KEY, clan_name TEXT, clan_owner_id INTEGER, '
            'clan_balance INTEGER)')
        self.conn.commit()

    def add_user(self, user_id, **kwargs):
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = list(kwargs.values())
        self.cursor.execute(f'INSERT INTO users (id, {fields}) VALUES (?, {placeholders})', (user_id, *values))
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def update_user(self, user_id, **kwargs):
        fields = ', '.join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())
        self.cursor.execute(f'UPDATE users SET {fields} WHERE id = ?', (*values, user_id))
        self.conn.commit()

    def create_user(self, user_id, first_name, drug_count=0, is_admin=0, is_banned=0, last_use_time=None,
                    last_casino=None,
                    last_find=None, clan_member=None, clan_invite=None):
        self.cursor.execute(
            'INSERT INTO users (id, first_name, drug_count, last_use_time, is_admin, is_banned, last_casino, last_find,'
            'clan_member, clan_invite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, first_name, drug_count, last_use_time, is_admin, is_banned, last_casino, last_find, clan_member,
             clan_invite))
        self.conn.commit()

    def update_last_use_time(self, user_id, time):
        self.cursor.execute('UPDATE users SET last_use_time = ? WHERE id = ?', (time, user_id))
        self.conn.commit()

    def update_drug_count(self, user_id, count):
        self.cursor.execute('UPDATE users SET drug_count = drug_count + ? WHERE id = ?', (count, user_id))
        self.conn.commit()

    def get_top_users(self, limit=None):
        query = 'SELECT id, drug_count FROM users ORDER BY drug_count DESC'
        params = ()
        if limit is not None:
            query += ' LIMIT ?'
            params = (limit,)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_clan_by_name(self, clan_name):
        self.cursor.execute('SELECT * FROM clans WHERE clan_name = ?', (clan_name,))
        return self.cursor.fetchone()

    def get_clan_by_id(self, clan_id):
        self.cursor.execute('SELECT * FROM clans WHERE clan_id = ?', (clan_id,))
        return self.cursor.fetchone()

    def update_clan_balance_by_owner(self, clan_owner_id, new_balance):
        self.cursor.execute('UPDATE clans SET clan_balance = ? WHERE clan_owner_id = ?', (new_balance, clan_owner_id))
        self.conn.commit()

    def create_clan(self, clan_id, clan_name, clan_owner_id, clan_balance):
        self.cursor.execute('INSERT INTO clans (clan_id, clan_name, clan_owner_id, clan_balance) VALUES (?, ?, ?, ?)',
                            (clan_id, clan_name, clan_owner_id, clan_balance))
        self.conn.commit()

    def get_all_chats(self):
        self.cursor.execute('SELECT chat_id FROM chats')
        return [chat[0] for chat in self.cursor.fetchall()]

    def update_clan_owner(self, clan_id, new_owner_id):
        self.cursor.execute('UPDATE clans SET clan_owner_id = ? WHERE clan_id = ?', (new_owner_id, clan_id))
        self.conn.commit()

    def get_clan_members(self, clan_id):
        self.cursor.execute('SELECT * FROM users WHERE clan_member = ?', (clan_id,))
        return self.cursor.fetchall()

    def update_user_clan_invite(self, user_id, clan_id):
        self.cursor.execute('UPDATE users SET clan_invite = ? WHERE id = ?', (clan_id, user_id))
        self.conn.commit()

    def remove_user_from_clan(self, user_id):
        self.cursor.execute('UPDATE users SET clan_member = 0 WHERE id = ?', (user_id,))
        self.conn.commit()

    def delete_clan(self, clan_id):
        self.cursor.execute('DELETE FROM clans WHERE clan_id = ?', (clan_id,))
        self.conn.commit()

    def update_users_with_clan_id(self, clan_id, **kwargs):
        fields = ', '.join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())
        self.cursor.execute(f'UPDATE users SET {fields} WHERE clan_member = ? OR clan_invite = ?',
                            (*values, clan_id, clan_id))
        self.conn.commit()

    def add_chat(self, chat_id):
        self.cursor.execute('INSERT OR IGNORE INTO chats (chat_id, is_ads_enable) VALUES (?, ?)', (chat_id, 1))
        self.conn.commit()

    def get_top_clans(self, limit=10):
        self.cursor.execute('SELECT clan_name, clan_balance FROM clans ORDER BY clan_balance DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
