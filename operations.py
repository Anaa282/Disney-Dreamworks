from sqlalchemy.ext.asyncio import AsyncSession, async_session
from sqlalchemy.future import select
from fastapi import HTTPException
from models import *
from schemas import PeliculaCreate, PersonajeCreate, PersonajeResponse
from database import async_session
from sqlalchemy.orm import joinedload

#PELICULAS


async def create_pelicula(db: AsyncSession, pelicula: PeliculaCreate):
    nueva = Pelicula(**pelicula.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

async def get_peliculas(db: AsyncSession):
    result = await db.execute(select(Pelicula).where(Pelicula.activa==True))
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

    result = await db.execute(
        select(Pelicula).where(Pelicula.titulo == personaje.pelicula.titulo)
    )
    pelicula_obj = result.scalar_one_or_none()


    if not pelicula_obj:
        raise HTTPException(status_code=404, detail="Película no encontrada")


    nuevo = Personaje(
        nombre=personaje.nombre,
        protagonista=personaje.protagonista,
        pelicula_id=pelicula_obj.id,
        activo=personaje.activo,
        img_url=personaje.img_url
    )

    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)


    result = await db.execute(
        select(Personaje)
        .options(joinedload(Personaje.pelicula))
        .where(Personaje.id == nuevo.id)
    )
    personaje_con_pelicula = result.scalar_one()


    return PersonajeResponse(
        id=personaje_con_pelicula.id,
        nombre=personaje_con_pelicula.nombre,
        protagonista=personaje_con_pelicula.protagonista,
        pelicula=personaje_con_pelicula.pelicula.titulo  # Solo el string
    )




async def get_personajes(db: AsyncSession):
    result = await db.execute(select(Personaje).where(Personaje.activo == True))
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
            return None

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

        personaje.activo = False
        await session.commit()
        return personaje