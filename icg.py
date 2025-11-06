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
        self._l = 0  # Contador para etiquetas
        self._buffer: List[Triplo] = []  # Buffer para reordenar triplos
        self._buffering = False  # Flag para saber si estamos en modo buffer

    # -------- generación básica --------
    def _next_idx(self) -> int:
        self._i += 1
        return self._i

    def new_temp(self) -> str:
        self._t += 1
        return f"t{self._t}"

    def new_label(self, prefix: str = "L") -> str:
        """
        Genera una nueva etiqueta única (L1, L2, ...)
        """
        self._l += 1
        return f"{prefix}{self._l}"

    def free_temp(self, temp_name: str):
        """
        Devuelve un temporal (tX) a la pila para ser reutilizado.
        Por ahora es un placeholder para compatibilidad con parser.py
        """
        # No hace nada en esta versión simplificada
        pass

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
        triplo = Triplo(
            idx,
            str(op),
            str(arg1) if arg1 is not None else None,
            str(arg2) if arg2 is not None else None,
            str(res) if res is not None else None,
        )
        
        # Si estamos en modo buffering, guardar en el buffer
        if self._buffering:
            self._buffer.append(triplo)
        else:
            self.rows.append(triplo)
        
        return res
    
    def start_buffering(self):
        """Inicia el modo buffer para guardar triplos temporalmente"""
        self._buffering = True
        self._buffer.clear()
    
    def end_buffering(self):
        """Termina el modo buffer y retorna los triplos guardados"""
        self._buffering = False
        buffered = self._buffer.copy()
        self._buffer.clear()
        return buffered
    
    def insert_triplos(self, triplos: List[Triplo]):
        """Inserta una lista de triplos en la tabla"""
        self.rows.extend(triplos)
    
    def mark_position(self) -> int:
        """Marca la posición actual en la tabla de triplos"""
        return len(self.rows)

    def error(self, lexeme: str = None, message: str = None):
        """
        Registrar un triplo de ERROR con DO y DF vacíos (compilador, no intérprete).
        El mensaje se guarda en tu error_table (no aquí).
        """
        # OP=ERROR; DO="", DF=""
        self.add("ERROR")

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
          - ERROR: DO = "", DF = ""   (requisito del compilador)
        IF_FALSE_GOTO queda por defecto como DO = res (etiqueta), DF = condición (arg1).
        """
        rows = []
        for r in self.rows:
            op = r.op
            DO = r.res or ""
            
            # --- LÓGICA DE DF MODIFICADA (PARA COINCIDIR CON PDF) ---
            
            # Caso 1: Acumulador (Ej: ADD, t1, 5, t1)
            #   DO (r.res) es 't1'. r.arg1 es 't1'.
            #   No queremos "t1, 5", solo queremos "5".
            if r.res is not None and r.res == r.arg1 and r.arg2 is not None:
                DF = r.arg2 or ""
            
            # Caso 2: Binario estándar (no usado en tu parser, pero bueno tenerlo)
            elif r.arg1 and r.arg2:
                DF = f"{r.arg1}, {r.arg2}"
            
            # Caso 3: Unario (Ej: :=, 7, None, t1) o (:=, t1, None, $1ITA)
            else:
                DF = r.arg1 or r.arg2 or ""
            # --- FIN DE LÓGICA MODIFICADA ---

            if op == "GOTO":
                DO, DF = (r.arg1 or ""), ""
            elif op == "LABEL":
                DO, DF = (r.arg1 or ""), ""
            elif op == "PRINT":
                DO, DF = (r.arg1 or ""), ""
            elif op == "ERROR":
                DO, DF = "", ""

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
        self._l = 0  # Resetear contador de etiquetas
        self._buffer.clear()
        self._buffering = False

    @property
    def triplos(self):
        """Alias para compatibilidad con código existente"""
        return self.rows

