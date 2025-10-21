# icg.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Triplo:
    idx: int
    op: str
    arg1: Optional[str]   # fuente 1 (interno)
    arg2: Optional[str]   # fuente 2 (interno)
    res: Optional[str]    # destino (interno)

class TriploTable:
    def __init__(self):
        self.rows: List[Triplo] = []
        self._i = 0
        self._t = 0

    # -------- generación básica --------
    def _next_idx(self) -> int:
        self._i += 1
        return self._i

    def new_temp(self) -> str:
        self._t += 1
        return f"t{self._t}"

    def add(self, op: str, arg1=None, arg2=None, res=None, note=None):
        """
        API usada por el parser:
          op  : operación (ADD, SUB, :=, GT, IF_FALSE_GOTO, LABEL, GOTO, PRINT, READ, ERROR, ...)
          arg1: fuente 1 (izq / condición / stdin)
          arg2: fuente 2 (der)  [opcional]
          res : destino (temporal tX, identificador, etiqueta)
          note: ignorado (ya no hay columna NOTE), se acepta por compatibilidad
        """
        idx = self._next_idx()
        self.rows.append(
            Triplo(
                idx,
                str(op),
                str(arg1) if arg1 is not None else None,
                str(arg2) if arg2 is not None else None,
                str(res) if res is not None else None,
            )
        )
        return res

    def error(self, lexeme: str, message: str):
        # Registramos como OP=ERROR; DO y DF sin nota (solo columnas pedidas)
        self.add("ERROR", arg1=lexeme, arg2=None, res="-")

    # -------- salida para UI (estilo maestra) --------
    def headers(self):
        # Solo estas 4 columnas
        return ["#", "OP", "DO", "DF"]

    def to_rows(self):
        """
        Mapeo a la notación pedida:
          - DO (Dato Objeto)   -> destino
          - DF (Dato Fuente)   -> fuentes (arg1 [, arg2])
        Casos especiales para que “se lea natural”:
          - GOTO : DO = etiqueta (arg1), DF = ""
          - LABEL: DO = etiqueta (arg1), DF = ""
          - PRINT: DO = valor (arg1),    DF = ""
        IF_FALSE_GOTO queda como DO = etiqueta (res), DF = condición (arg1).
        """
        rows = []
        for r in self.rows:
            op = r.op
            DO = r.res or ""
            DF = f"{r.arg1}, {r.arg2}" if (r.arg1 and r.arg2) else (r.arg1 or r.arg2 or "")

            if op == "GOTO":
                DO, DF = (r.arg1 or ""), ""
            elif op == "LABEL":
                DO, DF = (r.arg1 or ""), ""
            elif op == "PRINT":
                DO, DF = (r.arg1 or ""), ""
            # READ típicamente sería DO = id (res) y DF = stdin (arg1); queda con el mapping por defecto.

            rows.append({
                "#": r.idx,
                "OP": op,
                "DO": DO,
                "DF": DF,
            })
        return rows

    # -------- salida consola (opcional) --------
    def pretty(self) -> str:
        lines = ["# | OP        | DO           | DF",
                 "--+-----------+--------------+---------------------"]
        for row in self.to_rows():
            idx = f"{row['#']:<2}"
            op  = f"{row['OP']:<9}"
            do  = f"{row['DO']:<12}"
            df  = f"{row['DF']:<19}"
            lines.append(f"{idx}| {op} | {do} | {df}")
        return "\n".join(lines)

    # -------- util --------
    def clear(self):
        self.rows.clear()
        self._i = 0
        self._t = 0
