from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Pelicula(Base):
    __tablename__ = "peliculas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    genero = Column(String)
    anio = Column(Integer)
    estudio = Column(String)
    activa = Column(Boolean, default=True)

class Personaje(Base):
    __tablename__ = "personajes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    protagonista = Column(Boolean)
    pelicula = Column(String)
    activo = Column(Boolean, default=True)
