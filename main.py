
from fastapi import HTTPException, FastAPI, Request, Depends, Form, Query
from sqlalchemy.orm import selectinload
from sqlalchemy.testing import db
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
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
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.post("/peliculas/", response_model=PeliculaResponse)
async def crear_pelicula(data: PeliculaCreate):
    async with async_session() as session:
        nueva = Pelicula(**data.dict())
        session.add(nueva)
        await session.commit()
        await session.refresh(nueva)
        return nueva


@app.get("/peliculas/", response_model=List[PeliculaResponse])
async def leer_peliculas():
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.activa == True))

        return result.scalars().all()

@app.get("/peliculas/view", response_class=HTMLResponse)
async def ver_peliculas(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Pelicula).where(Pelicula.activa == True))
    peliculas = result.scalars().all()
    return templates.TemplateResponse("peliculas.html", {"request": request,"peliculas": peliculas})


@app.get("/peliculas/crear", response_class=HTMLResponse)
async def mostrar_formulario(request: Request):
    return templates.TemplateResponse("crear_pelicula.html", {"request": request})




@app.post("/peliculas/crear")
async def crear_pelicula(
    request: Request,
    titulo: str = Form(...),
    genero: str = Form(...),
    anio: int = Form(...),
    estudio: str = Form(...),
    img_url: str = Form(""),
    session: AsyncSession = Depends(get_async_session)
):
    await crear_pelicula_form(session, titulo, genero, anio, estudio, img_url)
    return RedirectResponse(url="/peliculas/view", status_code=303)

@app.get("/peliculas/{pelicula_id}/personajes", response_class=HTMLResponse)
async def personajes_de_pelicula(pelicula_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Personaje).where(Personaje.pelicula_id == pelicula_id, Personaje.activo == True))
    personajes = result.scalars().all()

    return templates.TemplateResponse("personajes_pelicula.html", {"request": request, "personajes": personajes})

@app.get("/peliculas/{id}", response_model=PeliculaResponse)
async def leer_pelicula(id: int):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.id == id))
        pelicula = result.scalar_one_or_none()
        if pelicula is None:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        return pelicula



@app.get("/peliculas/editar/{pelicula_id}")
async def mostrar_formulario(
    request: Request,
    pelicula_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    pelicula = await obtener_peli_id(session, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return templates.TemplateResponse("editar_pelicula.html", {"request": request, "pelicula": pelicula})

@app.post("/peliculas/editar/{pelicula_id}")
async def editar_pelicula(
    request: Request,
    pelicula_id: int,
    titulo: str = Form(...),
    genero: str = Form(...),
    anio: int = Form(...),
    estudio: str = Form(...),
    img_url: str = Form(""),
    session: AsyncSession = Depends(get_async_session)
):
    pelicula = await obtener_peli_id(session, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    await editar_pelicula_html(session, pelicula, titulo, genero, anio, estudio, img_url)
    return RedirectResponse(url="/peliculas/view", status_code=303)




@app.post("/peliculas/eliminar/{pelicula_id}")
async def eliminar_pelicula(pelicula_id: int, session: AsyncSession = Depends(get_async_session)):
    exito = await eliminar_pelicula_html(session, pelicula_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return RedirectResponse(url="/peliculas/view", status_code=303)


@app.get("/peliculas/filtrar/estudio", response_class=HTMLResponse)
async def buscar_peliculas_por_estudio(
    request: Request,
    estudio: str = Query(...),
    session: AsyncSession = Depends(get_async_session)
):
    peliculas = await buscar_por_estudio(session, estudio)
    return templates.TemplateResponse("peliculas.html", {"request": request, "peliculas": peliculas})



@app.get("/historial/peliculas", response_class=HTMLResponse)
async def ver_historial_peliculas(request: Request, session: AsyncSession = Depends(get_async_session)):
    historial = await historial_eliminacion_peliculas(session)
    return templates.TemplateResponse("historial_pelis.html", {"request": request, "historial": historial})

#----------------------------------------------------------------------------------------------------------------------------

@app.post("/personajes/", response_model=PersonajeResponse)
async def crear_personaje(data: PersonajeCreate):
    async with async_session() as session:
        nuevo = await create_personaje(session, data)
        return nuevo


@app.get("/crear-personaje-form", response_class=HTMLResponse)
async def mostrar_formulario_personaje(request: Request, session: AsyncSession = Depends(get_async_session)):
    peliculas = await get_peliculas_activas(session)
    return templates.TemplateResponse("crear_personaje.html", {"request": request, "peliculas": peliculas})


@app.post("/personajes/crear")
async def crear_personaje_post(
    request: Request,
    nombre: str = Form(...),
    pelicula_id: int = Form(...),
    protagonista: str = Form(None),
    img_url: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    await crear_personaje_form(session, nombre, pelicula_id, protagonista, img_url)
    return RedirectResponse("/personajes/view", status_code=303)




@app.get("/personajes/view", response_class=HTMLResponse)
async def mostrar_personajes_html(request: Request, session: AsyncSession = Depends(get_async_session)):
    personajes = await get_personajes(session)
    return templates.TemplateResponse("personajes.html", {"request": request, "personajes": personajes})


@app.get("/personajes/editar/{personaje_id}")
async def mostrar_formulario_edicion_personaje(
    request: Request,
    personaje_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    personaje = await get_personaje_por_id(session, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    peliculas = await get_peliculas(session)

    return templates.TemplateResponse("editar_personaje.html", {
        "request": request,
        "personaje": personaje,
        "peliculas": peliculas
    })


@app.post("/personajes/editar/{personaje_id}")
async def editar_personaje(
    personaje_id: int,
    nombre: str = Form(None),
    img_url: str = Form(None),
    protagonista: str = Form(None),
    pelicula_id: int = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    personaje = await get_personaje_por_id(session, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    await editar_personaje_form(session, personaje, nombre, img_url, protagonista, pelicula_id)
    return RedirectResponse(url="/personajes/view", status_code=303)



@app.post("/personajes/eliminar/{personaje_id}")
async def eliminar_personaje(personaje_id: int, session: AsyncSession = Depends(get_async_session)):
    personaje = await get_personaje_por_id(session, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    await eliminar_historial(session, personaje)
    return RedirectResponse(url="/personajes/view", status_code=303)


@app.get("/personajes/filtrar/protagonistas", response_class=HTMLResponse)
async def ver_protagonistas(request: Request, session: AsyncSession = Depends(get_async_session)):
    personajes = await get_protagonistas(session)
    return templates.TemplateResponse("personajes.html", {"request": request, "personajes": personajes})



@app.get("/historial/personajes", response_class=HTMLResponse)
async def ver_historial_personajes(request: Request, session: AsyncSession = Depends(get_async_session)):
    historial = await get_historial_personajes(session)
    return templates.TemplateResponse("historial_personajes.html", {"request": request, "historial": historial})

#----------------------------------------------------------------------------------------------------------------------------------------------
@app.get("/info/desarrollador", response_class=HTMLResponse)
async def vista_desarrollador(request: Request):
    return templates.TemplateResponse("desarrollador.html", {"request": request})

@app.get("/diseno")
async def diseno(request: Request):
    return templates.TemplateResponse("disenio.html", {"request": request})

@app.get("/planeacion")
async def planeacion(request: Request):
    return templates.TemplateResponse("planeacion.html", {"request": request})

@app.get("/objetivo")
async def objetivo(request: Request):
    return templates.TemplateResponse("objetivo.html", {"request": request})