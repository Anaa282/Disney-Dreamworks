from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from models import *
import operations as ops
import asyncio
from database import engine, Base


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": "Error",
            "detail": exc.detail,
            "path": request.url.path,
        },
    )

# ENDPOINTS PELICULAS

@app.get("/peliculas")
def get_all_peliculas():
    return ops.read_all_peliculas()

@app.get("/peliculas/{id}")
def get_one_pelicula(id: int):
    pelicula = ops.read_one_pelicula(id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return pelicula

@app.post("/peliculas")
def create_pelicula(pelicula: Pelicula):
    return ops.new_pelicula(pelicula)

@app.put("/peliculas/{id}")
def update_pelicula(id: int, datos: PeliculaUpdate):
    actualizada = ops.modify_pelicula(id, datos.model_dump(exclude_unset=True))
    if not actualizada:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return actualizada

@app.delete("/peliculas/{id}")
def eliminar_pelicula(id: int):
    ops.delete_pelicula(id)
    return {"mensaje": "Película eliminada"}

@app.get("/peliculas/buscar/estudio/{estudio}")
def buscar_por_estudio(estudio: str):
    return ops.buscar_pelicula_por_estudio(estudio)

@app.get("/peliculas/filtrar/genero/{genero}")
def filtrar_por_genero(genero: str):
    return ops.filtrar_peliculas_por_genero(genero)


# ENDPOINTS PERSONAJES

@app.get("/personajes")
def get_all_personajes():
    return ops.read_all_personajes()

@app.get("/personajes/{id}")
def get_one_personaje(id: int):
    personaje = ops.read_one_personaje(id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return personaje

@app.post("/personajes")
def create_personaje(personaje: Personaje):
    return ops.new_personaje(personaje)

@app.put("/personajes/{id}")
def update_personaje(id: int, datos: PersonajeUpdate):
    actualizado = ops.modify_personaje(id, datos.model_dump(exclude_unset=True))
    if not actualizado:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    return actualizado

@app.delete("/personajes/{id}")
def eliminar_personaje(id: int):
    ops.delete_personaje(id)
    return {"mensaje": "Personaje eliminado"}

@app.get("/personajes/buscar/pelicula/{pelicula}")
def buscar_por_pelicula(pelicula: str):
    return ops.buscar_personaje_por_pelicula(pelicula)

@app.get("/personajes/filtrar/protagonistas")
def filtrar_protagonistas():
    return ops.filtrar_personajes_protagonistas()



