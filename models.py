from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Pelicula(Base):
    __tablename__ = "peliculas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    genero = Column(String)
    anio = Column(Integer)
    estudio = Column(String)
    activa = Column(Boolean, default=True)
    img_url = Column(String)

    personajes = relationship("Personaje", back_populates="pelicula")

class Personaje(Base):
    __tablename__ = "personajes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    protagonista = Column(Boolean)
    pelicula_id = Column(Integer, ForeignKey("peliculas.id"))
    activo = Column(Boolean, default=True)
    img_url = Column(String)

    pelicula = relationship("Pelicula", back_populates="personajes")


class HistorialEliminacionPeliculas(Base):
    __tablename__ = "historial_eliminaciones_peliculas"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    nombre = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)

class HistorialEliminacionPersonajes(Base):
    __tablename__ = "historial_eliminaciones_personajes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    nombre = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
