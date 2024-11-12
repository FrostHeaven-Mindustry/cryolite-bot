from config import DATABASE_URL
from errors import UniqueError

from sqlalchemy import Column, BigInteger, String, ForeignKey, ARRAY, JSON, Boolean, select, update
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from asyncio import run

from sqlalchemy.exc import IntegrityError

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


class User(Base):
    """
    Discord user database model
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    clan_id: Mapped[int] = mapped_column(nullable=False, default=0)

    cryolite: Mapped[int] = mapped_column(nullable=False, default=0)
    ice_dust: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    boost_points: Mapped[int] = mapped_column(nullable=False, default=0)

    is_admin: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    has_js: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    ips = Column(ARRAY(String, dimensions=1))


class Player(Base):
    """
    Mindustry player database model
    """
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='SET DEFAULT'))
    banned_until: Mapped[int] = mapped_column(BigInteger)
    names: Mapped[list[str]] = mapped_column(ARRAY(String, dimensions=1))


class PlayerStats(Base):
    """
    Player`s statistic
    """
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


class Clan(Base):
    """
    Clan
    """
    __tablename__ = 'clans'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))
    title: Mapped[str] = mapped_column(unique=True)
    prefix: Mapped[str] = mapped_column(String(3), unique=True)
    slogan: Mapped[str]
    emblem_url: Mapped[str]

    way_three: Mapped[dict] = mapped_column(JSON, nullable=True)
    buildings: Mapped[dict] = mapped_column(JSON, nullable=True)

    async def members(self):
        return await db.scalars(select(User).where(User.clan_id == self.id))

    async def members_count(self):
        return len(list(await self.members()))

    async def edit(self, clan_title, prefix, slogan, emblem_url):
        if clan_title is not None:
            self.title = clan_title
        if prefix is not None:
            self.prefix = prefix
        if slogan is not None:
            self.slogan = slogan
        if emblem_url is not None:
            self.emblem_url = emblem_url
        try:
            await db.scalar(update(Clan),
                            [{'id': self.id,
                              'title': self.title,
                              'prefix': self.prefix,
                              'slogan': self.slogan,
                              'emblem_url': self.emblem_url}])
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise UniqueError('clan_edit')

    async def member_in_clan(self, user_id):
        user = await get_user(user_id)
        return self.id == user.clan_id


async def recreate_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_user(user_id: int):
    a = True
    try:
        db.add(User(user_id=user_id))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        a = False
    return a


async def get_user(user_id):
    user = await db.scalar(select(User).where(User.user_id == user_id))
    return user


async def kick_member(user_id):
    await db.execute(update(User).where(User.user_id == user_id).values(clan_id=0))
    await db.commit()


async def join_clan(user_id, clan_title):
    clan = await get_clan_by_title(clan_title)
    await db.execute(update(User).where(User.user_id == user_id).values(clan_id=clan.id))
    await db.commit()


async def create_clan(title, prefix, slogan, emblem_url, owner):
    clan = Clan(title=title, prefix=prefix, slogan=slogan, owner=owner, emblem_url=emblem_url)
    try:
        db.add(clan)
        await db.commit()
        await join_clan(owner, title)
    except IntegrityError:
        await db.rollback()
        raise UniqueError('clan_edit')


async def get_all_clans():
    return await db.scalars(select(Clan))


async def get_clan_by_title(title):
    return await db.scalar(select(Clan).where(Clan.title == title))


async def get_clan_by_id(id):
    return await db.get(Clan, id)


async def is_clan_exist(title):
    clan = await db.scalar(select(Clan).where(Clan.title == title))
    return clan is not None


async def in_clan(user_id):
    user = await db.scalar(select(User).where(User.user_id == user_id))
    return bool(user.clan_id)


async def get_user_clan(user_id):
    return await db.scalar(select(Clan).where(Clan.owner == user_id))


if __name__ == '__main__':
    run(recreate_db())
