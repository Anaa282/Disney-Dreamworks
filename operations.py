from sqlalchemy.ext.asyncio import AsyncSession, async_session
from sqlalchemy.future import select
from fastapi import HTTPException
from models import *
from schemas import PeliculaCreate, PersonajeCreate


#PELICULAS


async def create_pelicula(db: AsyncSession, pelicula: PeliculaCreate):
    nueva = Pelicula(**pelicula.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

async def get_peliculas(db: AsyncSession):
    result = await db.execute(select(Pelicula))
    return result.scalars().all()

async def get_pelicula_by_id(db: AsyncSession, pelicula_id: int):
    result = await db.execute(select(Pelicula).where(Pelicula.id == pelicula_id))
    pelicula = result.scalar_one_or_none()
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return pelicula

async def modificar_pelicula(id: int, nueva_data: dict):
    async with async_session() as session:
        query = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = query.scalar_one_or_none()
        if not pelicula:
            return None  # No existe

        for campo, valor in nueva_data.items():
            setattr(pelicula, campo, valor)

        await session.commit()
        await session.refresh(pelicula)  # Refresca desde DB
        return pelicula

async def eliminar_pelicula(id: int):
    async with async_session() as session:
        query = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = query.scalar_one_or_none()
        if not pelicula:
            return None

        pelicula.activa = False  # Eliminar trazablemente
        await session.commit()
        return pelicula


async def buscar_peliculas_por_estudio(estudio: str):
    async with async_session() as session:
        query = await session.execute(
            select(Pelicula).where(Pelicula.estudio.ilike(estudio))
        )
        return query.scalars().all()

async def filtrar_peliculas_por_genero(genero: str):
    async with async_session() as session:
        query = await session.execute(
            select(Pelicula).where(Pelicula.genero.ilike(genero))
        )
        return query.scalars().all()


# PERSONAJES


async def create_personaje(db: AsyncSession, personaje: PersonajeCreate):
    nuevo = Personaje(**personaje.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo

async def get_personajes(db: AsyncSession):
    result = await db.execute(select(Personaje))
    return result.scalars().all()

async def get_personaje_by_id(db: AsyncSession, personaje_id: int):
    result = await db.execute(select(Personaje).where(Personaje.id == personaje_id))
    personaje = result.scalar_one_or_none()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return personaje

async def modificar_personaje(id: int, nueva_data: dict):
    async with async_session() as session:
        query = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = query.scalar_one_or_none()
        if not personaje:
            return None  # No encontrado

        for campo, valor in nueva_data.items():
            setattr(personaje, campo, valor)

        await session.commit()
        await session.refresh(personaje)
        return personaje

async def eliminar_personaje(id: int):
    async with async_session() as session:
        query = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = query.scalar_one_or_none()
        if not personaje:
            return None

        personaje.activo = False  # Eliminación lógica (trazable)
        await session.commit()
        return personaje