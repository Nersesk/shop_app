from .configs import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def unit_of_work():
    engine = create_async_engine(settings.DATABASE_URL_asyncpg)
    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session: AsyncSession = session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
    finally:
        await session.close()



class UnitOfWork:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL_asyncpg)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def __aenter__(self):
        self.session: AsyncSession = self.session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
