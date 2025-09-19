class SymbolTable:
    def __init__(self):
        self.symbols = {}  # lexema -> tipo

    def clear(self):
        self.symbols.clear()

    def add(self, lexema, tipo):
        self.symbols[lexema] = tipo

    def exists(self, lexema):
        return lexema in self.symbols

    def get(self, lexema):
        return self.symbols.get(lexema)

    def rows(self):
        return [(k, v) for k, v in self.symbols.items()]


class ErrorTable:
    def __init__(self):
        self.errors = []       # [{Token, Lexema, Renglón, Descripción}]
        self.counter = 0       # Para ES1, ES2, ...

    def clear(self):
        self.errors.clear()
        self.counter = 0

    def _next_code(self):
        self.counter += 1
        return f"ES{self.counter}"

    def add(self, token, lexema, renglon, descripcion):
        """
        - token: puedes pasar None o '' y se autoasigna ES#
        - No se repite la combinación (Lexema, Renglón).
        """
        # Evitar repetición de (Lexema, Renglón)
        for e in self.errors:
            if e['Lexema'] == lexema and e['Renglón'] == renglon:
                return

        code = token if token else self._next_code()
        # Asegurar unicidad de Token también
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
