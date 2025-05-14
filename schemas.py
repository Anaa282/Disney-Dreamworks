from pydantic import BaseModel


class PeliculaBase(BaseModel):
    titulo: str
    genero: str
    anio: int
    estudio: str
    activa: bool = True

class PeliculaCreate(PeliculaBase):
    activo: bool = True
    pass

class PeliculaOut(PeliculaBase):
    id: int

    class Config:
        orm_mode = True





class PersonajeBase(BaseModel):
    nombre: str
    protagonista: bool
    pelicula: str
    activo: bool = True

class PersonajeCreate(PersonajeBase):
    activo: bool = True
    pass

class PersonajeOut(PersonajeBase):
    id: int
class PersonajeUpdate(BaseModel):
    nombre: str | None = None
    protagonista: bool | None = None
    pelicula: str | None = None
    activo: bool | None = None

    class Config:
        orm_mode = True
