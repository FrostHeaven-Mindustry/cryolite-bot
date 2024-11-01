from config import DATABASE_URL

from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, Boolean, Float, Null, ARRAY
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs


engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    clan_id = Column(Integer, default=Null)

    cryolite = Column(Integer, nullable=False, default=0)
    ice_dust = Column(BigInteger, nullable=False, default=0)
    boost_points = Column(Integer, nullable=False, default=0)

    is_admin = Column(Boolean, nullable=False, default=False)
    has_js = Column(Boolean, nullable=False, default=False)

    ips = Column(ARRAY(String, dimensions=1))


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(24), nullable=False, unique=True)
    user_id = Column(BigInteger, default=Null)
    names = Column(ARRAY(String, dimensions=1))

    user = relationship()


Base.metadata.create_all(bind=engine)


def string(text):
    return ("'" + text + "'") if isinstance(text, str) else str(text)


def create_user(user_id: int):  # Здесь мы добавляем аккаунт пользователя в БД
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
