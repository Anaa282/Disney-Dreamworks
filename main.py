
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

# Crear película
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


    nueva_pelicula = Pelicula(
        titulo=titulo,
        genero=genero,
        anio=anio,
        estudio=estudio,
        img_url=img_url,
        activa=True

    )
    session.add(nueva_pelicula)
    await session.commit()

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
@app.get("/peliculas/editar/{pelicula_id}")
async def mostrar_formulario_edicion_pelicula(
    request: Request,
    pelicula_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.get(Pelicula, pelicula_id)
    if not result:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    return templates.TemplateResponse("editar_pelicula.html", {
        "request": request,
        "pelicula": result
    })



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
    pelicula = await session.get(Pelicula, pelicula_id)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")


    pelicula.titulo = titulo or pelicula.titulo
    pelicula.genero = genero or pelicula.genero
    pelicula.anio = anio or pelicula.anio
    pelicula.estudio = estudio or pelicula.estudio
    pelicula.img_url = img_url or pelicula.img_url

    await session.commit()
    return RedirectResponse(url="/peliculas/view", status_code=303)

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

@app.post("/peliculas/eliminar/{pelicula_id}")
async def eliminar_pelicula(pelicula_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Pelicula).where(Pelicula.id == pelicula_id))
    pelicula = result.scalars().first()
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    historial = HistorialEliminacionPeliculas(
        tipo="películas",
        nombre=pelicula.titulo,
        fecha=datetime.utcnow()
    )
    session.add(historial)

    await session.delete(pelicula)
    await session.commit()
    return RedirectResponse(url="/peliculas/view", status_code=303)


@app.get("/peliculas/buscar_por_estudio/{estudio}", response_model=List[PeliculaResponse])
async def buscar_por_estudio(estudio: str):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.estudio == estudio, Pelicula.activa == True))
        return result.scalars().all()
@app.get("/peliculas/filtrar/estudio", response_class=HTMLResponse)
async def buscar_peliculas_por_estudio(
    request: Request,
    estudio: str = Query(...),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Pelicula).where(Pelicula.estudio.ilike(f"%{estudio}%")))
    peliculas = result.scalars().all()
    return templates.TemplateResponse("peliculas.html", {"request": request, "peliculas": peliculas})

@app.get("/peliculas/filtrar_por_genero/{genero}", response_model=List[PeliculaResponse])
async def filtrar_por_genero(genero: str):
    async with async_session() as session:
        result = await session.execute(select(Pelicula).where(Pelicula.genero == genero, Pelicula.activa == True))
        return result.scalars().all()

@app.get("/historial/peliculas", response_class=HTMLResponse)
async def ver_historial_peliculas(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(HistorialEliminacionPeliculas)
        .where(HistorialEliminacionPeliculas.tipo == "peliculas")
        .order_by(HistorialEliminacionPeliculas.fecha.desc())
    )
    historial = result.scalars().all()
    return templates.TemplateResponse("historial_pelis.html", {"request": request, "historial": historial})


#----------------------------------------------------------------------------------------------------------------------------

@app.post("/personajes/", response_model=PersonajeResponse)
async def crear_personaje(data: PersonajeCreate):
    async with async_session() as session:
        nuevo = await create_personaje(session, data)
        return nuevo

@app.get("/crear-personaje-form", response_class=HTMLResponse)
async def mostrar_formulario_personaje(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Pelicula).where(Pelicula.activa == True))
    peliculas = result.scalars().all()
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
    protagonista_bool = True if protagonista == "on" else False

    nuevo = Personaje(
        nombre=nombre,
        pelicula_id=pelicula_id,
        protagonista=protagonista_bool,
        img_url=img_url,
        activo=True
    )
    session.add(nuevo)
    await session.commit()
    return RedirectResponse("/personajes/view", status_code=303)



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
@app.get("/personajes/editar/{personaje_id}")
async def mostrar_formulario_edicion_personaje(
    request: Request,
    personaje_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    personaje_result = await session.execute(select(Personaje).where(Personaje.id == personaje_id))
    personaje = personaje_result.scalars().first()

    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    peliculas_result = await session.execute(select(Pelicula))
    peliculas = peliculas_result.scalars().all()

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
    result = await session.execute(select(Personaje).where(Personaje.id == personaje_id))
    personaje = result.scalars().first()

    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    if nombre:
        personaje.nombre = nombre
    if img_url is not None:
        personaje.img_url = img_url

    personaje.protagonista = protagonista == "on"
    personaje.pelicula_id = pelicula_id

    await session.commit()
    return RedirectResponse(url="/personajes/view", status_code=303)


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

@app.post("/personajes/eliminar/{personaje_id}")
async def eliminar_personaje(personaje_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Personaje).where(Personaje.id == personaje_id))
    personaje = result.scalars().first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")


    historial = HistorialEliminacionPersonajes(
        tipo="personaje",
        nombre=personaje.nombre,
        fecha=datetime.utcnow()
    )
    session.add(historial)

    await session.delete(personaje)
    await session.commit()
    return RedirectResponse(url="/personajes/view", status_code=303)


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

@app.get("/personajes/filtrar/protagonistas", response_class=HTMLResponse)
async def ver_protagonistas(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Personaje).options(selectinload(Personaje.pelicula)).where(Personaje.protagonista == True, Personaje.activo == True))
    personajes = result.scalars().all()
    return templates.TemplateResponse("personajes.html", {"request": request, "personajes": personajes})


@app.get("/info/desarrollador", response_class=HTMLResponse)
async def vista_desarrollador(request: Request):
    return templates.TemplateResponse("desarrollador.html", {"request": request})
@app.get("/historial/personajes", response_class=HTMLResponse)
async def ver_historial_personajes(request: Request, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(HistorialEliminacionPersonajes)
        .where(HistorialEliminacionPersonajes.tipo == "personaje")
        .order_by(HistorialEliminacionPersonajes.fecha.desc())
    )
    historial = result.scalars().all()
    return templates.TemplateResponse("historial_personajes.html", {"request": request, "historial": historial})

