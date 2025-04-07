from pydantic import BaseModel, Field
from typing import Optional

class Pelicula(BaseModel):
    titulo: str = Field(..., min_length=1)
    anio: int = Field(..., gt=1900)
    estudio: str
    genero: str
    activa: bool=True

class PeliculaconId(Pelicula):
    id: int

class PeliculaUpdate(BaseModel):
    titulo: Optional[str]=None
    anio: Optional[int]=None
    estudio: Optional[str]=None
    genero: Optional[str]=None
    activa: Optional[bool]=None

class Personaje(BaseModel):
    nombre: str = Field(...,min_length=1)
    protagonista: bool
    pelicula: str

class PersonajeUpdate(BaseModel):
    nombre: Optional[str]=None
    protagonista: Optional[bool]=None
    pelicula: Optional[str]=None



