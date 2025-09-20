from collections import OrderedDict

class SymbolTable:
    def __init__(self):
        self.symbols = OrderedDict()  # preserva orden

    def clear(self):
        self.symbols.clear()

    def add(self, lexema, tipo):
        self.symbols[lexema] = tipo

    def exists(self, lexema):
        return lexema in self.symbols

    def get(self, lexema):
        return self.symbols.get(lexema)

    def rows(self):
        return list(self.symbols.items())


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
        # Evita duplicar por (Lexema, Renglón, Descripción)
        for e in self.errors:
            if e['Lexema'] == lexema and e['Renglón'] == renglon and e['Descripción'] == descripcion:
                return
        code = token or self._next_code()
        used = {e['Token'] for e in self.errors}
        while code in used:
            code = self._next_code()
        self.errors.append({
            "Token": code,
            "Lexema": lexema,
            "Renglón": renglon,
            "Descripción": descripcion
        })

    def rows(self):
        return [(e['Token'], e['Lexema'], e['Renglón'], e['Descripción']) for e in self.errors]


class LexemeTable:
    """
    Tabla de TODOS los lexemas que aparecen (operadores, ;, IDs, etc.)
    Para los IDs, luego del parse completamos el 'Tipo'.
    """
    def __init__(self):
        self.items = OrderedDict()  # lexema -> tipo_o_None (preserva orden)

    def clear(self):
        self.items.clear()

    def add(self, lexema, tipo=None):
        if lexema not in self.items:     # queremos 1a aparición
            self.items[lexema] = tipo

    def set_type_if_id(self, lexema, tipo):
        if lexema in self.items:
            self.items[lexema] = tipo

    def rows(self):
        return [(k, (v if v else "")) for k, v in self.items.items()]
