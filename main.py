from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, engine, Base
import models
import operations
from schemas import PeliculaCreate, PeliculaOut, PersonajeCreate, PersonajeOut
from fastapi.middleware.cors import CORSMiddleware

# Crear tablas
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_models()



async def get_db():
    async with SessionLocal() as session:
        yield session



@app.post("/peliculas/", response_model=PeliculaOut)
async def crear_pelicula(pelicula: PeliculaCreate, db: AsyncSession = Depends(get_db)):
    return await operations.create_pelicula(db, pelicula)

@app.get("/peliculas/", response_model=list[PeliculaOut])
async def listar_peliculas(db: AsyncSession = Depends(get_db)):
    return await operations.get_peliculas(db)

@app.get("/peliculas/{pelicula_id}", response_model=PeliculaOut)
async def obtener_pelicula(pelicula_id: int, db: AsyncSession = Depends(get_db)):
    return await operations.get_pelicula_by_id(db, pelicula_id)

@app.post("/personajes/", response_model=PersonajeOut)
async def crear_personaje(personaje: PersonajeCreate, db: AsyncSession = Depends(get_db)):
    return await operations.create_personaje(db, personaje)

@app.get("/personajes/", response_model=list[PersonajeOut])
async def listar_personajes(db: AsyncSession = Depends(get_db)):
    return await operations.get_personajes(db)

@app.get("/personajes/{personaje_id}", response_model=PersonajeOut)
async def obtener_personaje(personaje_id: int, db: AsyncSession = Depends(get_db)):
    return await operations.get_personaje_by_id(db, personaje_id)

@app.get("/ping-db")
async def ping_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(1))
    return {"status": "Conexión exitosa"}
