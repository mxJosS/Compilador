# tables.py
from collections import OrderedDict

# ---------------------------
# Tabla de Símbolos
# ---------------------------
class SymbolTable:
    def __init__(self):
        self.symbols = OrderedDict()  # preserva orden de inserción

    def clear(self):
        self.symbols.clear()

    def add(self, lexema: str, tipo: str):
        self.symbols[lexema] = tipo

    def exists(self, lexema: str) -> bool:
        return lexema in self.symbols

    def get(self, lexema: str):
        return self.symbols.get(lexema)

    def rows(self):
        # [(lexema, tipo), ...]
        return list(self.symbols.items())


# ---------------------------
# Tabla de Errores (semánticos)
#   - dedup por (Lexema, Renglón, Descripción)
#   - permite múltiples errores distintos en el mismo renglón
# ---------------------------
class ErrorTable:
    def __init__(self):
        self.errors = []
        self.counter = 0

    def clear(self):
        self.errors.clear()
        self.counter = 0

    def _next_code(self):
        self.counter += 1
        return f"ES{self.counter}"

    def add(self, token, lexema, renglon, descripcion):
        # Evitar duplicados exactos
        for e in self.errors:
            if (e['Lexema'] == lexema and
                e['Renglón'] == renglon and
                e['Descripción'] == descripcion):
                return
        code = token or self._next_code()
        self.errors.append({
            "Token": code,
            "Lexema": lexema,
            "Renglón": renglon,
            "Descripción": descripcion
        })

    def rows(self):
        # [(token, lexema, renglon, descripcion), ...]
        return [(e['Token'], e['Lexema'], e['Renglón'], e['Descripción'])
                for e in self.errors]


# ---------------------------
# Tabla de Lexemas (para UI)
#   - guarda TODOS los lexemas que aparecen (IDs, operadores, ';', literales…)
#   - el tipo se completa luego si el lexema es un ID declarado
# ---------------------------
class LexemeTable:
    def __init__(self):
        self.items = OrderedDict()  # lexema -> tipo|None

    def clear(self):
        self.items.clear()

    def add(self, lexema, tipo=None):
        # No sobreescribimos la primera aparición
        if lexema not in self.items:
            self.items[lexema] = tipo

    def set_type_if_id(self, lexema, tipo):
        if lexema in self.items:
            self.items[lexema] = tipo

    def rows(self):
        # [(lexema, tipo_o_vacio), ...]
        return [(k, (v if v else "")) for k, v in self.items.items()]


# ---------------------------
# Instancias globales (para importar)
# ---------------------------
symbol_table = SymbolTable()
error_table = ErrorTable()
lexeme_table = LexemeTable()
