
from fastapi import HTTPException, FastAPI, Request, Depends
from sqlalchemy.orm import selectinload
from sqlalchemy.testing import db
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from models import Personaje, Pelicula
from database import async_session, get_async_session
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from schemas import *
from sqlalchemy import func, select
from fastapi.responses import JSONResponse
from operations import *

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Crear película
@app.post("/peliculas/", response_model=PeliculaResponse)
async def crear_pelicula(data: PeliculaCreate):
    async with async_session() as session:
        nueva = Pelicula(**data.dict())
        session.add(nueva)
        await session.commit()
        await session.refresh(nueva)
        return nueva

# Leer todas las películas activas
@app.get("/peliculas/", response_model=List[PeliculaResponse])
async def leer_peliculas():
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.activa == True))

        return result.scalars().all()

# Leer película por ID
@app.get("/peliculas/{id}", response_model=PeliculaResponse)
async def leer_pelicula(id: int):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = result.scalar_one_or_none()
        if pelicula is None:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        return pelicula

# Actualizar película
@app.put("/peliculas/{id}", response_model=PeliculaResponse)
async def actualizar_pelicula(id: int, datos: PeliculaUpdate):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = result.scalar_one_or_none()
        if pelicula is None:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        for key, value in datos.dict(exclude_unset=True).items():
            setattr(pelicula, key, value)
        await session.commit()
        await session.refresh(pelicula)
        return pelicula


@app.delete("/peliculas/{id}")
async def eliminar_pelicula(id: int):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = result.scalar_one_or_none()
        if pelicula is None:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        pelicula.activa = False
        await session.commit()
        return {"mensaje": "Película marcada como inactiva"}


@app.get("/peliculas/buscar_por_estudio/{estudio}", response_model=List[PeliculaResponse])
async def buscar_por_estudio(estudio: str):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.estudio == estudio, Pelicula.activa == True))
        return result.scalars().all()

@app.get("/peliculas/filtrar_por_genero/{genero}", response_model=List[PeliculaResponse])
async def filtrar_por_genero(genero: str):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.genero == genero, Pelicula.activa == True))
        return result.scalars().all()


@app.post("/personajes/", response_model=PersonajeResponse)
async def crear_personaje(data: PersonajeCreate):
    async with async_session() as session:
        nuevo = await create_personaje(session, data)
        return nuevo


@app.get("/personajes/", response_model=List[PersonajeResponse])
async def leer_personajes():
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.activo==True).options(selectinload(Personaje.pelicula)))
        personajes = result.scalars().all()

        if not personajes:
            return JSONResponse(status_code=404, content={"message": "No hay personajes activos."})


        personajes_con_nombre = [
            PersonajeResponse(
                id=p.id,
                nombre=p.nombre,
                protagonista=p.protagonista,
                pelicula=p.pelicula.titulo if p.pelicula else None
            )
            for p in personajes
        ]
        return personajes_con_nombre


@app.get("/personajes/view", response_class=HTMLResponse)
async def mostrar_personajes_html(request: Request, session: AsyncSession = Depends(get_async_session)):
    personajes = await get_personajes(session)
    return templates.TemplateResponse("personajes.html", {"request": request, "personajes": personajes})

@app.get("/personajes/{id}", response_model=PersonajeCreate)
async def leer_personaje(id: int):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = result.scalar_one_or_none()
        if personaje is None:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        return personaje


@app.put("/personajes/{id}", response_model=PersonajeCreate)
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


@app.delete("/personajes/{id}")
async def eliminar_personaje(id: int):
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.id == id))
        personaje = result.scalar_one_or_none()
        if personaje is None:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        personaje.activo = False
        await session.commit()
        return {"mensaje": "Personaje marcado como inactivo"}


@app.get("/personajes/buscar_por_pelicula/{titulo}", response_model=List[PersonajeCreate])
async def buscar_por_pelicula(titulo: str):
    async with async_session() as session:

        result = await session.execute(
            select(Pelicula).where(func.lower(Pelicula.titulo) == titulo.lower(), Pelicula.activa == True)
        )
        pelicula = result.scalar_one_or_none()

        if pelicula is None:
            raise HTTPException(status_code=404, detail="Película no encontrada")


        result = await session.execute(
            select(Personaje).where(Personaje.pelicula_id == pelicula.id, Personaje.activo == True)
        )
        return result.scalars().all()



@app.get("/personajes/protagonistas", response_model=List[PersonajeCreate])
async def filtrar_protagonistas():
    async with async_session() as session:
        result = await session.execute(select(Personaje).where(Personaje.protagonista == True, Personaje.activo == True))
        return result.scalars().all()

