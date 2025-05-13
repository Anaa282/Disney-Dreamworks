from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from models import Pelicula, Personaje
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