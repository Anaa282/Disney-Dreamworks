from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://peliculas_db_t797_user:A23XVNpV3RsG6jkmv6viV9SvECa0Do7E@dpg-d0htcc3uibrs739ohak0-a/peliculas_db_t797"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()