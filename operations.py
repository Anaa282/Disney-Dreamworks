import csv
from typing import Optional, List
from models import *


PELICULAS_CSV = "peliculas.csv"
PERSONAJES_CSV = "personajes.csv"


P_FIELDS = ["id", "titulo", "genero", "anio", "estudio", "activa"]
PJ_FIELDS = ["id", "nombre", "protagonista", "pelicula", "activo"]



def get_next_id(filename: str) -> int:
    try:
        with open(filename, mode="r") as file:
            reader = csv.DictReader(file)
            return max(int(row["id"]) for row in reader) + 1
    except (FileNotFoundError, ValueError):
        return 1


# PELICULAS

def read_all_peliculas() -> list[PeliculaconId]:
    with open("peliculas.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        peliculas = []
        for row in reader:
            if row["activa"] == "True":
                pelicula = PeliculaconId(
                    id=int(row["id"]),
                    titulo=row["titulo"],
                    anio=int(row["anio"]),
                    estudio=row["estudio"],
                    genero=row["genero"],
                    activa=True
                )
                peliculas.append(pelicula)
        return peliculas


def read_one_pelicula(id: int) -> Optional[PeliculaconId]:
    with open(PELICULAS_CSV) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row["id"]) == id and row["activa"].lower() == "true":
                return PeliculaconId(
                    id=int(row["id"]),
                    titulo=row["titulo"],
                    genero=row["genero"],
                    anio=int(row["anio"]),
                    estudio=row["estudio"],
                    activa=True
                )


def new_pelicula(p: Pelicula) -> PeliculaconId:
    id = get_next_id(PELICULAS_CSV)
    data = p.model_dump()
    data["id"] = id
    data["activa"] = True
    pelicula = PeliculaconId(**data)
    with open(PELICULAS_CSV, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=P_FIELDS)
        writer.writerow(pelicula.model_dump())
    return pelicula


def modify_pelicula(id: int, cambios: dict) -> Optional[PeliculaconId]:
    peliculas = read_all_peliculas()
    modificada = None
    for i, peli in enumerate(peliculas):
        if peli.id == id:
            for campo, valor in cambios.items():
                setattr(peliculas[i], campo, valor)
            modificada = peliculas[i]
            break

    if modificada:
        with open(PELICULAS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=P_FIELDS)
            writer.writeheader()
            for peli in peliculas:
                writer.writerow(peli.model_dump())
        return modificada

def delete_pelicula(id: int):
    peliculas = read_all_peliculas()
    for peli in peliculas:
        if peli.id == id:
            peli.activa = False

    with open(PELICULAS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=P_FIELDS)
        writer.writeheader()
        for peli in peliculas:
            writer.writerow(peli.model_dump())

def buscar_pelicula_por_estudio(estudio: str):
    return [p for p in read_all_peliculas() if p.estudio.lower() == estudio.lower()]

def filtrar_peliculas_por_genero(genero: str):
    return [p for p in read_all_peliculas() if p.genero.lower() == genero.lower()]


# PERSONAJES

def read_all_personajes() -> list[PersonajeconId]:
    personajes = []
    with open("personajes.csv", "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["activo"].lower() == "true":
                personaje = PersonajeconId(
                    id=int(row["id"]),
                    nombre=row["nombre"],
                    protagonista=row["protagonista"].lower() == "true",
                    pelicula=row["pelicula"],
                    activo=True
                )
                personajes.append(personaje)
    return personajes



def read_one_personaje(id: int) -> Optional[PersonajeconId]:
    with open(PERSONAJES_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if int(row["id"]) == id and row["activo"].lower() == "true":
                    return PersonajeconId(
                        id=int(row["id"]),
                        nombre=row["nombre"],
                        protagonista=row["protagonista"].lower() == "true",
                        pelicula=row["pelicula"],
                        activo=True
                    )
            except (ValueError, KeyError):
                print(f"Error en la fila: {row}")
    return None


def new_personaje(p: Personaje) -> PersonajeconId:
    id = get_next_id(PERSONAJES_CSV)
    personaje = PersonajeconId(
        id=id,
        nombre=p.nombre,
        protagonista=p.protagonista,
        pelicula=p.pelicula,
        activo=True
    )
    with open(PERSONAJES_CSV, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PJ_FIELDS)
        writer.writerow(personaje.model_dump())
    return personaje


def modify_personaje(id: int, cambios: dict) -> Optional[PersonajeconId]:
    personajes = read_all_personajes()
    modificado = None
    for i, pj in enumerate(personajes):
        if pj.id == id:
            for campo, valor in cambios.items():
                setattr(personajes[i], campo, valor)
            modificado = personajes[i]
            break

    if modificado:
        with open(PERSONAJES_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=PJ_FIELDS)
            writer.writeheader()
            for pj in personajes:
                writer.writerow(pj.model_dump())
        return modificado

def delete_personaje(id: int):
    personajes = read_all_personajes()
    for pj in personajes:
        if pj.id == id:
            pj.activo = False

    with open(PERSONAJES_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PJ_FIELDS)
        writer.writeheader()
        for pj in personajes:
            writer.writerow(pj.model_dump())

def buscar_personaje_por_pelicula(pelicula: str):
    return [p for p in read_all_personajes() if p.pelicula.lower() == pelicula.lower()]

def filtrar_personajes_protagonistas():
    return [p for p in read_all_personajes() if p.protagonista]

