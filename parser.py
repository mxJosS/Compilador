# parser.py
import ply.yacc as yacc
from lexer import tokens
from tables import symbol_table, error_table
from icg import TriploTable   # <--- OK

# ===== Triplos =====
trip = TriploTable()          # <--- OK

precedence = (
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MOD'),
)

def tipos_compatibles_igual(t1, t2):
    if t1 is None or t2 is None:
        return False
    return t1 == t2

def es_cadena(t):
    return t == 'meow'

def es_num(t):
    return t in ('cat', 'cats')

def p_programa(p):
    '''programa : lista_sentencias_opt'''
    # no-op (la tabla de triplos queda en 'trip')
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
    pass

# -------- Declaraciones --------
def p_declaracion(p):
    '''declaracion : TIPO ID PUNTOYCOMA'''
    tipo = p[1]
    lex  = p[2]
    if symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(2), "Declaración duplicada")
        trip.error(lex, "Declaración duplicada")  # también en triplos (ERROR con DO/DF vacíos)
    else:
        symbol_table.add(lex, tipo)

# -------- Expresiones base --------
def p_expresion_group(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]

def p_expresion_id(p):
    '''expresion : ID'''
    nombre = p[1]
    ln     = p.lineno(1)
    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, ln, "Variable indefinida")
        trip.error(nombre, "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln, 'place': nombre}
    else:
        p[0] = {'lexema': nombre, 'tipo': symbol_table.get(nombre), 'lineno': ln, 'place': nombre}

def p_expresion_badid(p):
    '''expresion : BADID'''
    ln = p.lineno(1)
    error_table.add(None, p[1], ln, "Variable indefinida")
    trip.error(p[1], "Variable indefinida")
    p[0] = {'lexema': p[1], 'tipo': None, 'lineno': ln, 'place': p[1]}

def p_expresion_entero(p):
    '''expresion : ENTERO'''
    val = str(p[1])
    p[0] = {'lexema': val, 'tipo': 'cat', 'lineno': p.lineno(1), 'place': val}

def p_expresion_real(p):
    '''expresion : REAL'''
    val = str(p[1])
    p[0] = {'lexema': val, 'tipo': 'cats', 'lineno': p.lineno(1), 'place': val}

def p_expresion_cadena(p):
    '''expresion : CADENA'''
    val = p[1]
    p[0] = {'lexema': val, 'tipo': 'meow', 'lineno': p.lineno(1), 'place': val}

def p_expresion_unaria(p):
    '''expresion : MAS expresion
                 | MENOS expresion'''
    op = p[1]
    e  = p[2]
    if op == '-':
        t = trip.new_temp()
        trip.add('NEG', arg1=e['place'], arg2=None, res=t)
        p[0] = {'lexema': t, 'tipo': e['tipo'], 'lineno': e['lineno'], 'place': t}
    else:
        p[0] = {'lexema': e['lexema'], 'tipo': e['tipo'], 'lineno': e['lineno'], 'place': e['place']}

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MOD expresion'''
    izq, op, der = p[1], p[2], p[3]
    t1, t2       = izq['tipo'], der['tipo']

    if t1 is not None and t2 is not None and t1 != t2:
        error_table.add(None, izq['lexema'], izq['lineno'],
                        f"Incompatibilidad de tipos ({t1} <- {t2})")
        error_table.add(None, der['lexema'], der['lineno'],
                        f"Incompatibilidad de tipos ({t2} <- {t1})")
        trip.error(f"{izq['lexema']} {op} {der['lexema']}", "Incompatibilidad de tipos")

    if t1 == t2:
        tres = t1
    elif t1 is None:
        tres = t2
    elif t2 is None:
        tres = t1
    else:
        tres = None

    op_map = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV', '%':'MOD'}
    t = trip.new_temp()
    trip.add(op_map[op], arg1=izq['place'], arg2=der['place'], res=t)
    p[0] = {'lexema': t, 'tipo': tres, 'lineno': izq['lineno'], 'place': t}

# -------- Asignaciones --------
def p_asignacion_id(p):
    '''asignacion : ID ASIGNACION expresion PUNTOYCOMA'''
    nombre = p[1]
    ln     = p.lineno(1)

    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, ln, "Variable indefinida")
        trip.error(nombre, "Variable indefinida")
        # Limpieza de errores colaterales en la misma línea (tu comportamiento original)
        error_table.errors = [
            e for e in error_table.errors
            if not (e.get('Renglón') == ln and e.get('Lexema') != nombre)
        ]
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln, 'place': nombre}
        return

    tipo_izq = symbol_table.get(nombre)
    tipo_der = p[3]['tipo']  # puede ser None

    if tipo_der is not None and tipo_izq != tipo_der:
        msg = f"Incompatibilidad de tipos ({tipo_izq} <- {tipo_der})"
        error_table.add(None, nombre, ln, msg)
        trip.error(nombre, msg)

    rhs_place = p[3]['place']
    trip.add(':=', arg1=rhs_place, arg2=None, res=nombre)

    p[0] = {'lexema': nombre, 'tipo': tipo_izq, 'lineno': ln, 'place': nombre}

def p_asignacion_badid(p):
    '''asignacion : BADID ASIGNACION expresion PUNTOYCOMA'''
    ln = p.lineno(1)
    lhs = p[1]
    error_table.add(None, lhs, ln, "Variable indefinida")
    trip.error(lhs, "Variable indefinida")
    error_table.errors = [
        e for e in error_table.errors
        if not (e.get('Renglón') == ln and e.get('Lexema') != lhs)
    ]
    trip.add(':=', arg1=p[3].get('place'), arg2=None, res=lhs)
    p[0] = {'lexema': lhs, 'tipo': None, 'lineno': ln, 'place': lhs}

# -------- For --------
def p_ciclo_for(p):
    '''ciclo_for : FOR LPAREN asignacion condicion_opt PUNTOYCOMA asignacion RPAREN LBRACE lista_sentencias_opt RBRACE'''
    # Esquema clásico simplificado
    L_begin = f"L{len(trip.rows)+1}_for"
    L_end   = f"L{len(trip.rows)+2}_fend"
    trip.add('LABEL', arg1=L_begin, arg2=None, res='-')

    if p[4] is not None and isinstance(p[4], dict):
        cond_place = p[4].get('place')
    else:
        cond_place = None

    if cond_place is not None:
        # IF_FALSE_GOTO a L_end; en to_rows, DO=res (etiqueta) y DF=condición
        trip.add('IF_FALSE_GOTO', arg1=cond_place, arg2=None, res=L_end)

    # (tu flujo actual) — sin tocar resto para no afectar funcionalidad existente
    trip.add('GOTO', arg1=L_begin, arg2=None, res='-')
    trip.add('LABEL', arg1=L_end, arg2=None, res='-')

def p_condicion_opt(p):
    '''condicion_opt : expresion
                     | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = None

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    # Puedes agregar registro sintáctico si lo deseas:
    # if p is None: trip.error(None, "Fin de entrada inesperado")
    # else: trip.error(str(getattr(p, 'value', '?')), "Token inesperado")
    pass

parser = yacc.yacc(debug=False)
