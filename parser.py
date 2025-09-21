# parser.py
import ply.yacc as yacc
from lexer import tokens
from tables import symbol_table, error_table

# ---------------------------
# Precedencia
# ---------------------------
precedence = (
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MOD'),
)

# ---------------------------
# Utilidades de tipos
# ---------------------------
def tipos_compatibles_igual(t1, t2):
    """Devuelve True si son exactamente compatibles para operaciones numéricas."""
    if t1 is None or t2 is None:
        return False
    return t1 == t2

def es_cadena(t):
    return t == 'meow'

def es_num(t):
    return t in ('cat', 'cats')

# ---------------------------
# Gramática
# ---------------------------
def p_programa(p):
    '''programa : lista_sentencias_opt'''
    pass

def p_lista_sentencias_opt(p):
    '''lista_sentencias_opt : lista_sentencias
                            | empty'''
    pass

def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | ciclo_for
                 | expresion PUNTOYCOMA'''
    # Las expresiones ya registran errores semánticos internamente.
    pass

# -------- Declaraciones --------
def p_declaracion(p):
    '''declaracion : TIPO ID PUNTOYCOMA'''
    tipo = p[1]
    lex  = p[2]
    if symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(2), "Declaración duplicada")
    else:
        symbol_table.add(lex, tipo)

# Declaración con identificador mal formado -> Variable indefinida
def p_declaracion_badid(p):
    '''declaracion : TIPO BADID PUNTOYCOMA'''
    error_table.add(None, p[2], p.lineno(2), "Variable indefinida")

# -------- Asignaciones --------
def p_asignacion(p):
    '''asignacion : ID ASIGNACION expresion PUNTOYCOMA'''
    nombre = p[1]
    ln     = p.lineno(1)

    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, ln, "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln}
        return

    tipo_izq = symbol_table.get(nombre)
    tipo_der = p[3]['tipo']  # puede ser None si hubo indefinidas dentro

    # Solo reportar incompatibilidad si se conoce el tipo de la expresión
    if tipo_der is not None and tipo_izq != tipo_der:
        error_table.add(None, nombre, ln, f"Incompatibilidad de tipos ({tipo_izq} <- {tipo_der})")

    p[0] = {'lexema': nombre, 'tipo': tipo_izq, 'lineno': ln}

# -------- For (estructura mínima para no romper ejemplos) --------
def p_ciclo_for(p):
    '''ciclo_for : FOR LPAREN asignacion condicion_opt PUNTOYCOMA asignacion RPAREN LBRACE lista_sentencias_opt RBRACE'''
    pass

def p_condicion_opt(p):
    '''condicion_opt : expresion
                     | empty'''
    pass

# -------- Expresiones --------
def p_expresion_group(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]

def p_expresion_id(p):
    '''expresion : ID'''
    nombre = p[1]
    ln     = p.lineno(1)
    if not symbol_table.exists(nombre):
        # Se reporta UNA VEZ aquí; no se vuelve a reportar en la binaria
        error_table.add(None, nombre, ln, "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln}
    else:
        p[0] = {'lexema': nombre, 'tipo': symbol_table.get(nombre), 'lineno': ln}

# Identificador mal formado usado en expresión -> Variable indefinida
def p_expresion_badid(p):
    '''expresion : BADID'''
    ln = p.lineno(1)
    error_table.add(None, p[1], ln, "Variable indefinida")
    p[0] = {'lexema': p[1], 'tipo': None, 'lineno': ln}

def p_expresion_entero(p):
    '''expresion : ENTERO'''
    p[0] = {'lexema': str(p[1]), 'tipo': 'cat', 'lineno': p.lineno(1)}

def p_expresion_real(p):
    '''expresion : REAL'''
    p[0] = {'lexema': str(p[1]), 'tipo': 'cats', 'lineno': p.lineno(1)}

def p_expresion_cadena(p):
    '''expresion : CADENA'''
    p[0] = {'lexema': p[1], 'tipo': 'meow', 'lineno': p.lineno(1)}

def p_expresion_unaria(p):
    '''expresion : MAS expresion
                 | MENOS expresion'''
    # La unaria no cambia el tipo, solo lo propaga
    p[0] = {'lexema': p[2]['lexema'], 'tipo': p[2]['tipo'], 'lineno': p[2]['lineno']}

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MOD expresion'''
    izq, op, der = p[1], p[2], p[3]
    t1, t2       = izq['tipo'], der['tipo']

    # Nota: NO volvemos a reportar "Variable indefinida" aquí (eso ya lo hace ID/BADID)
    # Aquí solo incompatibilidades cuando ambos tipos son conocidos.
    if t1 is not None and t2 is not None and t1 != t2:
        # Cadena con numérico o numéricos distintos => reportar en los operandos
        # Registramos dos filas (como pide la rúbrica: múltiples errores en el mismo renglón)
        error_table.add(None, izq['lexema'], izq['lineno'],
                        f"Incompatibilidad de tipos ({t1} <- {t2})")
        error_table.add(None, der['lexema'], der['lineno'],
                        f"Incompatibilidad de tipos ({t2} <- {t1})")

    # Tipo resultante:
    if t1 == t2:
        tres = t1
    elif t1 is None:
        tres = t2
    elif t2 is None:
        tres = t1
    else:
        tres = None

    # El lexema que propagamos es el del operando izquierdo (no el operador)
    p[0] = {'lexema': izq['lexema'], 'tipo': tres, 'lineno': izq['lineno']}

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    # Silenciado: no reportamos errores de sintaxis (solo semánticos)
    pass

# ---------------------------
# Construcción del parser
# ---------------------------
parser = yacc.yacc(debug=False)
