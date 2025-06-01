from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Pelicula(Base):
    __tablename__ = "peliculas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    genero = Column(String)
    anio = Column(Integer)
    estudio = Column(String)
    activa = Column(Boolean, default=True)

    personajes = relationship("Personaje", back_populates="pelicula")

class Personaje(Base):
    __tablename__ = "personajes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    protagonista = Column(Boolean)
    pelicula = Column(Integer, ForeignKey("peliculas.id"))
    activo = Column(Boolean, default=True)

    pelicula = relationship("Pelicula", back_populates="personajes")
