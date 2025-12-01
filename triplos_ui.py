# triplos_ui.py
from parser import trip  # instancia global creada en parser.py


def reset_triplos_table():
    """
    Limpia la tabla de triplos y resetea contadores para que
    cada análisis empiece desde #1 sin arrastrar resultados previos.
    """
    trip.clear()


def get_triplos_table():
    """
    Devuelve metadatos y filas para la UI.
    Estructura: {"title": "Triplos", "headers": [...], "rows": [...]}
    """
    return {"title": "Triplos", "headers": trip.headers(), "rows": trip.to_rows()}


def get_triplos_raw():
    """
    Devuelve la lista interna de triplos (objetos Triplo) para
    que otros módulos (como el generador de ensamblador) puedan
    trabajar directamente con ellos.
    """
    return trip.triplos
