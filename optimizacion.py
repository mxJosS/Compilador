# optimizacion.py
"""
Módulo de optimización de código para el compilador de Autómatas II.

Técnica B: Instrucciones dependientes susceptibles de reorganización.
Idea (según los ejemplos de la unidad):
    - Si una asignación usa dentro de su expresión algo que ya se calculó antes
      en otra asignación, se reemplaza esa subexpresión por la variable que ya
      la almacena.

Ejemplo:
    a = z + 22;
    b = w - z + 22;

    =>

    a = z + 22;
    b = w - a;
"""

import re


_ASIGNACION_RE = re.compile(r'^\s*(\$\w+)\s*=\s*(.+);')


def _normalizar_expresion(expr: str) -> str:
    """
    Normaliza una expresión para poder compararla:
    - Elimina espacios.
    (Aquí podrías hacer más cosas si tu gramática lo requiere).
    """
    return expr.replace(" ", "")


def optimizar_dependencias(codigo: str) -> str:
    """
    Aplica la técnica B al código fuente recibido como texto completo.

    - Recorre el código línea por línea.
    - Solo intenta optimizar líneas que sean asignaciones simples:
        $ID = <expresión>;
    - Guarda expresiones calculadas en asignaciones anteriores y, si
      aparecen como subexpresión en una nueva asignación, las reemplaza
      por la variable que ya las tiene.

    No modifica líneas que no entren en ese patrón (for, llaves, etc.).
    """
    lineas = codigo.splitlines()

    # expr_normalizada -> nombre de la variable que la guarda
    expresiones_previas: dict[str, str] = {}

    nuevas_lineas: list[str] = []

    for linea in lineas:
        m = _ASIGNACION_RE.match(linea)

        if not m:
            # No es una asignación simple reconocida, la dejamos tal cual
            nuevas_lineas.append(linea)
            continue

        var = m.group(1)              # p.ej. $1ITA
        expr_original = m.group(2)    # p.ej. $1ITA * 3 + 550 - 30

        expr_norm = _normalizar_expresion(expr_original)
        expr_opt_norm = expr_norm

        # Buscamos subexpresiones que ya se hayan calculado antes
        for expr_prev_norm, var_prev in expresiones_previas.items():
            if expr_prev_norm in expr_opt_norm:
                expr_opt_norm = expr_opt_norm.replace(expr_prev_norm, var_prev)

        # Registramos la expresión ORIGINAL para reutilizarla después
        # (la idea es que si más adelante se usa tal cual, se sustituya).
        expresiones_previas[expr_norm] = var

        # En esta versión no reinsertamos espacios bonitos; podrías
        # mejorar el formateo si tu profe lo pide, pero funcionalmente
        # es correcto.
        expr_opt_final = expr_opt_norm

        nuevas_lineas.append(f"{var} = {expr_opt_final};")

    return "\n".join(nuevas_lineas)
