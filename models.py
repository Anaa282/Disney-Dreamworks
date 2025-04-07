from pydantic import BaseModel, Field
from typing import Optional

class Pelicula(BaseModel):
    titulo: str = Field(..., min_length=1)
    anio: int = Field(..., gt=1900)
    estudio: str = Field(..., min_length=1)
    genero: str = Field(..., min_length=1)


class PeliculaconId(Pelicula):
    id: int
    activa: bool=True

class PeliculaUpdate(BaseModel):
    titulo: Optional[str]=None
    anio: Optional[int]=None
    estudio: Optional[str]=None
    genero: Optional[str]=None


class Personaje(BaseModel):
    nombre: str = Field(...,min_length=1)
    protagonista: bool
    pelicula: str = Field(...,min_length=1)

class PersonajeconId(Personaje):
    id: int
    activo: bool=True

class PersonajeUpdate(BaseModel):
    nombre: Optional[str]=None
    protagonista: Optional[bool]=None
    pelicula: Optional[str]=None



