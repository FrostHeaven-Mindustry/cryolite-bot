from config import DATABASE_URL

from sqlalchemy import Column, BigInteger, String, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from asyncio import run


engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    clan_id: Mapped[int]

    cryolite: Mapped[int] = mapped_column(nullable=False, default=0)
    ice_dust: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    boost_points: Mapped[int] = mapped_column(nullable=False, default=0)

    is_admin: Mapped[bool] = Column(nullable=False, default=False)
    has_js: Mapped[bool] = Column(nullable=False, default=False)

    ips = Column(ARRAY(String, dimensions=1))


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    banned_until: Mapped[int] = mapped_column(BigInteger)
    names: Mapped[list[str]] = mapped_column(ARRAY(String, dimensions=1))

    user = relationship()


class PlayerStats(Base):
    __tablename__ = 'players_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(ForeignKey('players.uuid'))

    join_count: Mapped[int]

    blocks_built: Mapped[int]
    blocks_destroyed: Mapped[int]

    waves: Mapped[int]
    wins: Mapped[int]
    loses: Mapped[int]
    times_kicked: Mapped[int]
    times_banned: Mapped[int]


class Clans(Base):
    __tablename__ = 'clans'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    prefix: Mapped[str] = mapped_column(String(3))
    slogan: Mapped[str]
    emblem_url: Mapped[str]

    way_three: Mapped[JSON]
    buildings: Mapped[JSON]


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


run(create_db())


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
