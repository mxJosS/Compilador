# triplos_ui.py
from parser import trip  # instancia global creada en parser.py

def get_triplos_table():
    return {"title": "Triplos", "headers": trip.headers(), "rows": trip.to_rows()}
