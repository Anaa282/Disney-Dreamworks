
from fastapi import APIRouter, HTTPException, FastAPI
from sqlalchemy.ext.asyncio import async_session

from models import *
from database import async_session
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from schemas import *



app = FastAPI()
router = APIRouter()
app.include_router(router)

@router.post("/personajes/", response_model=PersonajeCreate)
async def crear_personaje(data: PersonajeCreate):
    async with async_session() as session:
        nuevo = Personaje(**data.dict())
        session.add(nuevo)
        await session.commit()
        await session.refresh(nuevo)
        return nuevo

# Leer todos los personajes activos
@router.get("/personajes/", response_model=List[PersonajeCreate])
async def leer_personajes():
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.activo == True))
        return result.scalars().all()

# Leer un personaje por ID
@router.get("/personajes/{id}", response_model=PersonajeCreate)
async def leer_personaje(id: int):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = result.scalar_one_or_none()
        if personaje is None:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        return personaje

# Actualizar personaje
@router.put("/personajes/{id}", response_model=PersonajeCreate)
async def actualizar_personaje(id: int, datos: PersonajeUpdate):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = result.scalar_one_or_none()
        if personaje is None:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(personaje, key, value)
        await session.commit()
        await session.refresh(personaje)
        return personaje

# Eliminar personaje (marcar como inactivo)
@router.delete("/personajes/{id}")
async def eliminar_personaje(id: int):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = result.scalar_one_or_none()
        if personaje is None:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        personaje.activo = False
        await session.commit()
        return {"mensaje": "Personaje marcado como inactivo"}

# Buscar personajes por película
@router.get("/personajes/buscar_por_pelicula/{titulo}", response_model=List[PersonajeCreate])
async def buscar_por_pelicula(titulo: str):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.pelicula == titulo, Personaje.activo == True))
        return result.scalars().all()

# Filtrar personajes que son protagonistas
@router.get("/personajes/protagonistas", response_model=List[PersonajeCreate])
async def filtrar_protagonistas():
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.protagonista == True, Personaje.activo == True))
        return result.scalars().all()

