from pydantic import BaseModel
from typing import Optional


class PeliculaBase(BaseModel):
    titulo: str
    genero: str
    anio: int
    estudio: str
    img_url:Optional[str] = None

class PeliculaCreate(PeliculaBase):
    pass

class PeliculaUpdate(BaseModel):
    titulo: str | None = None
    genero: str | None = None
    anio: int | None = None
    estudio: str | None = None

class PeliculaResponse(PeliculaBase):
    id: int
    activa: bool

class PeliculaNested(BaseModel):
    titulo: str


    class Config:
        from_attributes = True



class PersonajeBase(BaseModel):
    nombre: str
    protagonista: bool
    activo: bool = True
    img_url:Optional[str] = None

class PersonajeCreate(PersonajeBase):
    activo: bool = True
    pelicula: PeliculaNested
    pass

class PersonajeOut(PersonajeBase):
    id: int
    pelicula_id: int



class PersonajeUpdate(BaseModel):
    nombre: str | None = None
    protagonista: bool | None = None
    pelicula: str | None = None
    activo: bool | None = None
    img_url:Optional[str] = None

class PersonajeResponse(BaseModel):
    id: int
    nombre: str
    protagonista: bool
    pelicula: Optional[str] = None

    class Config:
        from_attributes = True
