from typing import List
from icg import Triplo


def generar_ensamblador(triplos: List[Triplo]) -> List[str]:
    """
    Traduce la lista de Triplos a código ensamblador 8086 (pseudo-ASM),
    siguiendo tus reglas. NO agrega encabezados ni labels extra.
    """
    asm: List[str] = []

    for t in triplos:
        op = t.op
        a1 = t.arg1 if t.arg1 is not None else "0"
        a2 = t.arg2 if t.arg2 is not None else "0"
        res = t.res or ""

        # -------- ASIGNACIÓN: res = a1 --------
        if op in (":=", "="):
            asm.append(f"MOV AX, {a1}")
            if res:
                asm.append(f"MOV {res}, AX")

        # -------- SUMA: res = a1 + a2 --------
        elif op == "ADD":
            asm.append(f"MOV AX, {a1}")
            asm.append(f"ADD AX, {a2}")
            if res:
                asm.append(f"MOV {res}, AX")

        # -------- RESTA: res = a1 - a2 --------
        elif op == "SUB":
            asm.append(f"MOV AX, {a1}")
            asm.append(f"SUB AX, {a2}")
            if res:
                asm.append(f"MOV {res}, AX")

        # -------- MULTIPLICACIÓN --------
        # MOV AL, a1
        # MOV BL, a2
        # MUL BL  ; resultado en AX
        elif op == "MUL":
            asm.append(f"MOV AL, {a1}")
            asm.append(f"MOV BL, {a2}")
            asm.append("MUL BL")
            if res:
                asm.append(f"MOV {res}, AX")

        # -------- DIVISIÓN --------
        # MOV AX, a1
        # MOV BL, a2
        # DIV BL  ; AL = cociente, AH = residuo
        elif op == "DIV":
            asm.append(f"MOV AX, {a1}")
            asm.append(f"MOV BL, {a2}")
            asm.append("DIV BL")
            if res:
                asm.append(f"MOV {res}, AL")

        # -------- MÓDULO --------
        elif op == "MOD":
            asm.append(f"MOV AX, {a1}")
            asm.append(f"MOV BL, {a2}")
            asm.append("DIV BL")
            if res:
                asm.append(f"MOV {res}, AH")

        # -------- COMPARACIONES --------
        elif op in {"GT", "GTE", "LT", "LTE", "EQ", "NEQ"}:
            asm.append(f"; CMP {a1} {op} {a2}")
            asm.append(f"MOV AX, {a1}")
            asm.append(f"CMP AX, {a2}")

        # -------- IF_FALSE_GOTO --------
        elif op == "IF_FALSE_GOTO":
            cond = a1
            label = res or a1
            asm.append(f"MOV AX, {cond}")
            asm.append("CMP AX, 0")
            asm.append(f"JE {label}")

        # -------- GOTO --------
        elif op == "GOTO":
            label = t.arg1 or res
            asm.append(f"JMP {label}")

        # -------- LABEL --------
        elif op == "LABEL":
            label = t.arg1 or res
            asm.append(f"{label}:")

        # -------- IO / ERRORES COMO COMENTARIO --------
        elif op == "PRINT":
            asm.append(f"; PRINT {a1}")
        elif op == "READ":
            asm.append(f"; READ {res}")
        elif op == "ERROR":
            asm.append("; ERROR de compilación (no se genera código)")

        # -------- OTROS --------
        else:
            asm.append(f"; Operador no soportado aún: {op}")

    return asm
