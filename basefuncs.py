from config import keys
from functools import wraps

import disnake
import psycopg2


def connect():
    return psycopg2.connect(
        dbname=keys['database']['name'],
        user=keys['database']['user'],
        password=keys['database']['password'],
        host=keys['database']['host'],
        port=keys['database']['port'])


def string(text):
    return ("'" + text + "'") if isinstance(text, str) else str(text)


def create_user(user: disnake.Member):  # Здесь мы добавляем аккаунт пользователя в БД
    con = connect()
    cur = con.cursor()
    a = True
    cur.execute(f"SELECT id FROM users WHERE id = {user.id}")
    account = cur.fetchone()
    if account:  # Проверяем, существует ли такой аккаунт
        a = False  # Если да, ничего не делаем
    else:
        cur.execute(f"INSERT INTO users(id) VALUES ({user.id})")
        con.commit()  # Если нет, создаём новый
    con.close()
    return a  # И говорим, был ли создан новый аккаунт


def get_from_db(table, column, value, *args):
    con = connect()
    cur = con.cursor()
    value = string(value)
    if column is None:
        value = column = 1
    cur.execute(f"SELECT {', '.join(args)} FROM {table} WHERE {column} = {value}")
    values = cur.fetchone()
    con.close()
    return values


def add_to_db(table, **values):
    con = connect()
    cur = con.cursor()
    cur.execute(
        f'INSERT INTO {table} ({', '.join([str(i) for i in values])}) VALUES ({', '.join([string(values[i]) for i in values])})')
    con.commit()
    con.close()


def update_db(table, column, value, **kwargs):
    con = connect()
    cur = con.cursor()
    if isinstance(value, str):
        value = "'" + value + "'"
    cur.execute(f"UPDATE {table} SET {', '.join(f'{i} = {kwargs[i]}' for i in kwargs)} WHERE {column} = {value}")
    con.commit()
    con.close()


def in_clan(uid):
    return get_from_db("users", "id", uid, "clan")[0]
