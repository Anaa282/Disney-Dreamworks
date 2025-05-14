from pydantic import BaseModel

class PeliculaBase(BaseModel):
    titulo: str
    genero: str
    anio: int
    estudio: str

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
