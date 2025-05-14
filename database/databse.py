import sqlite3
from pathlib import Path
from deep_translator import GoogleTranslator


import requests

BASE_DIR = Path(__name__).resolve().parent
base_url = "https://api.alquran.cloud/v1/surah/"


class DatabaseConnection:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.cursor, self.connection = self.connect()


    def connect(self) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
        connection = sqlite3.connect(BASE_DIR / self.database_path)
        cursor = connection.cursor()
        return cursor, connection

class DatabaseTables(DatabaseConnection):
    def __init__(self, database_path: str) -> None:
        super().__init__(database_path)

    def create(self, query:str) -> None:
        self.cursor.executescript(query)

db_table = DatabaseTables('database.db')
db_table.create('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT UNIQUE
);

CREATE TABLE IF NOT EXISTS praying(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    fajr DATETIME NOT NULL,
    dhuhr DATETIME NOT NULL,
    asr DATETIME NOT NULL,
    maghrib DATETIME NOT NULL,
    isha DATETIME NOT NULL,
    created_at DATE,
    timezone TEXT,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS surah(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    eng_name TEXT UNIQUE,
    eng_name_t TEXT,
    num_ayahs INTEGER,
    revelation_type TEXT
);
''')

class UsersRepo(DatabaseConnection):
    def get_user(self, chat_id: int) -> tuple | None:
        self.cursor.execute("SELECT id FROM users WHERE chat_id = ?;", (chat_id,))
        result = self.cursor.fetchone()
        return result

    def add_user(self, chat_id:int) -> None:
        query = 'INSERT INTO users(chat_id) VALUES (?);'

        if self.get_user(chat_id) is None:
            self.cursor.execute(query, (chat_id,))
            self.connection.commit()

from datetime import datetime

class PrayingRepo(DatabaseConnection):
    def reset_autoincrement(self):
        reset_query = 'DELETE FROM sqlite_sequence WHERE name="praying";'
        self.cursor.execute(reset_query)
        self.connection.commit()

    def add_praying(self,
                    location: str,
                    fajr: str,
                    dhuhr: str,
                    asr: str,
                    maghrib: str,
                    isha: str,
                    created_at: datetime,
                    timezone:str,
                    user_id:int,
                    ) -> None:




        delete_query = '''
                        DELETE FROM praying 
                        WHERE user_id = ?;
                        '''
        self.cursor.execute(delete_query, (user_id,))
        self.connection.commit()
        self.reset_autoincrement()

        check_query = '''
                    SELECT COUNT(*) FROM praying 
                    WHERE user_id = ? AND DATE(created_at) = ? AND timezone = ?;
                '''
        self.cursor.execute(check_query, (user_id, created_at, timezone))
        count = self.cursor.fetchone()[0]

        if count == 0:
            query = ('''INSERT INTO praying(location,fajr,dhuhr,asr,maghrib,isha,created_at,timezone,user_id)
                VALUES(?,?,?,?,?,?,?,?,?);
                ''')
            self.cursor.execute(query,(location,fajr,dhuhr,asr,maghrib,isha,created_at,timezone,user_id))
            self.connection.commit()
        #     print("New prayer record added.")
        # else:
        #     print("Record already exists for this user, date, and timezone.")


    def get_praying(self, user_id) -> dict | None:
        query = 'SELECT fajr,dhuhr,asr,maghrib,isha,created_at,timezone FROM praying WHERE user_id = ?'
        result = self.cursor.execute(query,(user_id,)).fetchone()
        if result:
            return {
                "Fajr": result[0],
                "Dhuhr": result[1],
                "Asr": result[2],
                "Maghrib": result[3],
                "Isha": result[4],
                'Day': result[5],
                'Timezone': result[6],
            }
        return None

    def get_user_timezone(self,user_id) -> str | None:
        query = 'SELECT location FROM praying WHERE user_id = ?'
        location = self.cursor.execute(query,(user_id,)).fetchone()
        return location

class SurahRepo(DatabaseConnection):
    def add_surah(self):
        url = "https://api.alquran.cloud/v1/surah"
        response = requests.get(url)

        if response.status_code == 200:
            surahs = response.json()


            for surah in surahs['data']:
                surah_name = surah['name']
                surah_eng_name = surah['englishName']
                surah_eng_name_t = surah['englishNameTranslation']
                surah_num_ayahs = surah['numberOfAyahs']
                surah_revelation_type = surah['revelationType']

                check_query = '''
                    SELECT COUNT(*) FROM surah
                    WHERE name = ? AND eng_name = ? AND eng_name_t = ?;
                '''
                self.cursor.execute(check_query, (surah_name,surah_eng_name,surah_eng_name_t))
                count = self.cursor.fetchone()[0]

                if count == 0:
                    query = ('''INSERT INTO surah(name,eng_name,eng_name_t,num_ayahs,revelation_type)
                        VALUES(?,?,?,?,?);
                    ''')
                    self.cursor.execute(query,(surah_name,surah_eng_name,surah_eng_name_t,surah_num_ayahs,surah_revelation_type))
            self.connection.commit()

    def get_surah_name(self):
        query = "SELECT id, eng_name FROM surah ORDER BY id ASC"
        surah_names = self.cursor.execute(query).fetchall()
        return [(surah[0], surah[1]) for surah in surah_names]

    def get_surah_info(self, chosen_surah_name):
        query = ('SELECT * from surah WHERE eng_name = ?;')
        data = self.cursor.execute(query,(chosen_surah_name,)).fetchone()
        surah_number = data[0]
        surah_name = data[1]
        surah_eng_name = data[2]
        surah_eng_name_t = data[3]
        surah_num_ayahs = data[4]
        surah_revelation_type = data[5]

        surah_uzbek_name_t = GoogleTranslator(source='en', target='uz').translate(surah_eng_name_t)

        return f"""Surah Ma'lumotlari:
-------------------
Surah raqami:    {surah_number}
Inglizcha nomi: {surah_eng_name}
Arabcha nomi:   {surah_name}
O'zbekcha nomi: {surah_uzbek_name_t}
Oyatlar soni:   {surah_num_ayahs}
Vahiy turi:     {surah_revelation_type}
        """

    def get_full_surah(self,surah_number):
        response = requests.get(f'{base_url}{surah_number}')
        data = response.json()
        ayahs = data['data']['ayahs']
        ayahs_list = []
        for ayah in ayahs:
            ayahs_list.append(ayah['text'])
        return ayahs_list

    def get_surah_transliteration(self, surah_number):
        response = requests.get(f'{base_url}{surah_number}/en.transliteration')
        data = response.json()
        ayahs = data['data']['ayahs']
        ayahs_list = []
        for ayah in ayahs:
            ayahs_list.append(ayah['text'])
        return ayahs_list



users_repo = UsersRepo(BASE_DIR/'database.db')
praying_repo = PrayingRepo(BASE_DIR/'database.db')
surah_repo = SurahRepo(BASE_DIR/'database.db')