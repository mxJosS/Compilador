import ply.yacc as yacc
from lexer import tokens
from tables import symbol_table, error_table
from icg import TriploTable

# ===== Triplos =====
trip = TriploTable()
for_stack = []

# ===== Precedencias =====
precedence = (
    ('left', 'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL', 'DIF'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MOD'),
)

# ===== Utiles de tipos =====
def tipos_compatibles_igual(t1, t2):
    if t1 is None or t2 is None:
        return False
    return t1 == t2

def es_cadena(t):
    return t == 'meow'

def es_num(t):
    return t in ('cat', 'cats')

# ===== Gramática =====
def p_programa(p):
    '''
    programa : lista_sentencias_opt
    '''
    # Marcar fin
    trip.add('HALT', res='...')

def p_lista_sentencias_opt(p):
    '''
    lista_sentencias_opt : lista_sentencias
                         | empty
    '''
    pass

def p_lista_sentencias(p):
    '''
    lista_sentencias : lista_sentencias sentencia
                     | sentencia
    '''
    pass

def p_sentencia(p):
    '''
    sentencia : declaracion
              | asignacion
              | ciclo_for
              | if_stmt
              | expresion PUNTOYCOMA
    '''
    pass

# -------- Declaraciones --------
def p_declaracion(p):
    '''
    declaracion : TIPO ID PUNTOYCOMA
    '''
    tipo = p[1]
    lex  = p[2]
    if symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(2), "Declaración duplicada")
        trip.error(lex, "Declaración duplicada")
    else:
        symbol_table.add(lex, tipo)

# -------- Expresiones base --------
def p_expresion_group(p):
    '''
    expresion : LPAREN expresion RPAREN
    '''
    p[0] = p[2]

def p_expresion_id(p):
    '''
    expresion : ID
    '''
    nombre = p[1]
    ln     = p.lineno(1)
    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, ln, "Variable indefinida")
        trip.error(nombre, "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln, 'place': nombre}
    else:
        p[0] = {'lexema': nombre, 'tipo': symbol_table.get(nombre), 'lineno': ln, 'place': nombre}

def p_expresion_badid(p):
    '''
    expresion : BADID
    '''
    ln = p.lineno(1)
    error_table.add(None, p[1], ln, "Variable indefinida")
    trip.error(p[1], "Variable indefinida")
    p[0] = {'lexema': p[1], 'tipo': None, 'lineno': ln, 'place': p[1]}

def p_expresion_entero(p):
    '''
    expresion : ENTERO
    '''
    val = str(p[1])
    p[0] = {'lexema': val, 'tipo': 'cat', 'lineno': p.lineno(1), 'place': val}

def p_expresion_real(p):
    '''
    expresion : REAL
    '''
    val = str(p[1])
    p[0] = {'lexema': val, 'tipo': 'cats', 'lineno': p.lineno(1), 'place': val}

def p_expresion_cadena(p):
    '''
    expresion : CADENA
    '''
    val = p[1]
    p[0] = {'lexema': val, 'tipo': 'meow', 'lineno': p.lineno(1), 'place': val}

def p_expresion_unaria(p):
    '''
    expresion : MAS expresion
              | MENOS expresion
    '''
    op = p[1]
    e  = p[2]
    if op == '-':
        # t = e ; t = NEG t
        t = trip.new_temp()
        trip.add(':=', arg1=e['place'], res=t)
        trip.add('NEG', arg1=t, res=t)
        trip.free_temp(e['place'])
        p[0] = {
            'lexema': f'{op}{e["lexema"]}',
            'tipo': e['tipo'],
            'lineno': e['lineno'],
            'place': t
        }
    else:
        # '+' unario: propaga
        p[0] = {
            'lexema': f'{op}{e["lexema"]}',
            'tipo': e['tipo'],
            'lineno': e['lineno'],
            'place': e['place']
        }

def p_expresion_binaria(p):
    '''
    expresion : expresion MAS expresion
              | expresion MENOS expresion
              | expresion MULT expresion
              | expresion DIV expresion
              | expresion MOD expresion
    '''
    izq, op, der = p[1], p[2], p[3]
    expr_str = f'{izq["lexema"]} {op} {der["lexema"]}'
    t1, t2   = izq['tipo'], der['tipo']

    # Tipado (sin errores extra por cadenas; solo propagación)
    if op in ('+', '-', '*', '/'):
        if t1 == 'meow' or t2 == 'meow':
            tres = 'meow'  # clave para que la asignación reporte (meow -----> cat)
        elif t1 is None:
            tres = t2
        elif t2 is None:
            tres = t1
        elif t1 == 'cats' or t2 == 'cats':
            tres = 'cats'
        elif t1 == 'cat' and t2 == 'cat':
            tres = 'cat'
        else:
            tres = None
    elif op == '%':
        if t1 == 'cat' and t2 == 'cat':
            tres = 'cat'
        else:
            tres = None
            if t1 is not None and t2 is not None and (t1 != 'cat' or t2 != 'cat'):
                error_table.add(None, expr_str, izq['lineno'], "Operador % requiere enteros (cat)")
                trip.error(expr_str, "Tipos no enteros en %")

    op_map = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV', '%':'MOD'}

    t = trip.new_temp()
    trip.add(':=', arg1=izq['place'], res=t)
    trip.add(op_map[op], arg1=t, arg2=der['place'], res=t)
    trip.free_temp(izq['place'])
    trip.free_temp(der['place'])

    p[0] = {'lexema': expr_str, 'tipo': tres, 'lineno': izq['lineno'], 'place': t}

def p_expresion_comparacion(p):
    '''
    expresion : expresion MAYOR expresion
              | expresion MENOR expresion
              | expresion MAYORIGUAL expresion
              | expresion MENORIGUAL expresion
              | expresion IGUAL expresion
              | expresion DIF expresion
    '''
    izq, op, der = p[1], p[2], p[3]
    expr_str = f'{izq["lexema"]} {op} {der["lexema"]}'

    t1, t2 = izq['tipo'], der['tipo']
    if t1 is not None and t2 is not None and t1 != t2:
        error_table.add(None, expr_str, izq['lineno'],
                        f"Incompatibilidad de tipos en comparación ({t1} vs {t2})")
        trip.error(expr_str, "Incompatibilidad de tipos")

    op_map = {'>': 'GT', '>=': 'GTE', '<': 'LT', '<=': 'LTE', '==': 'EQ', '!=': 'NEQ'}

    t = trip.new_temp()
    trip.add(':=', arg1=izq['place'], res=t)
    trip.add(op_map[op], arg1=t, arg2=der['place'], res=t)
    trip.free_temp(izq['place'])
    trip.free_temp(der['place'])

    p[0] = {'lexema': expr_str, 'tipo': 'boolean', 'lineno': izq['lineno'], 'place': t}

# -------- If (con/sin else) --------
def p_if_stmt(p):
    '''
    if_stmt : IF LPAREN expresion RPAREN LBRACE lista_sentencias_opt RBRACE
            | IF LPAREN expresion RPAREN LBRACE lista_sentencias_opt RBRACE ELSE LBRACE lista_sentencias_opt RBRACE
    '''
    cond = p[3]

    L_else = trip.new_label("L_else")
    L_end  = trip.new_label("L_end")

    trip.add('IF_FALSE_GOTO', arg1=cond['place'], res=L_else)

    if len(p) == 8:
        # if sin else
        trip.add('LABEL', arg1=L_else, res='-')
    else:
        # if con else
        trip.add('GOTO', arg1=L_end, res='-')
        trip.add('LABEL', arg1=L_else, res='-')
        trip.add('LABEL', arg1=L_end, res='-')

# -------- Asignaciones --------
def p_asignacion_id(p):
    '''
    asignacion : ID ASIGNACION expresion PUNTOYCOMA
    '''
    nombre = p[1]
    ln     = p.lineno(1)

    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, ln, "Variable indefinida")
        trip.error(nombre, "Variable indefinida")
        # Limpia errores colaterales de esa línea
        error_table.errors = [
            e for e in error_table.errors
            if not (e.get('Renglón') == ln and e.get('Lexema') != nombre)
        ]
        p[0] = {'lexema': nombre, 'tipo': None, 'lineno': ln, 'place': nombre}
        return

    tipo_izq = symbol_table.get(nombre)
    rhs      = p[3]
    tipo_der = rhs['tipo']               # puede ser None
    rhs_lex  = rhs['lexema']             # descriptivo
    rhs_line = rhs['lineno']

    # Si el RHS no tiene tipo (expresión inválida), marca error
    if tipo_der is None:
        msg = f"Incompatibilidad de tipos (desconocido -----> {tipo_izq})"
        error_table.add(None, rhs_lex, rhs_line, msg)
        trip.error(rhs_lex, msg)
    # Acepta widening cat -> cats; marca error para cats -> cat
    elif not (tipo_izq == tipo_der or (tipo_izq == 'cats' and tipo_der == 'cat')):
        msg = f"Incompatibilidad de tipos ({tipo_der} -----> {tipo_izq})"
        error_table.add(None, rhs_lex, rhs_line, msg)
        trip.error(rhs_lex, msg)

    # Emisión de triplos de asignación
    rhs_place = rhs['place']
    is_complex_expr = (rhs_place and rhs_place.startswith('t'))

    if is_complex_expr:
        trip.add(':=', arg1=rhs_place, res=nombre)
        trip.free_temp(rhs_place)
    else:
        t = trip.new_temp()
        trip.add(':=', arg1=rhs_place, res=t)
        trip.add(':=', arg1=t, res=nombre)
        trip.free_temp(t)

    p[0] = {'lexema': nombre, 'tipo': tipo_izq, 'lineno': ln, 'place': nombre}

def p_asignacion_badid(p):
    '''
    asignacion : BADID ASIGNACION expresion PUNTOYCOMA
    '''
    ln = p.lineno(1)
    lhs = p[1]
    error_table.add(None, lhs, ln, "Variable indefinida")
    trip.error(lhs, "Variable indefinida")
    error_table.errors = [
        e for e in error_table.errors
        if not (e.get('Renglón') == ln and e.get('Lexema') != lhs)
    ]
    trip.add(':=', arg1=p[3].get('place'), res=lhs)
    p[0] = {'lexema': lhs, 'tipo': None, 'lineno': ln, 'place': lhs}

# -------- For (marcadores + reordenación) --------
def p_ciclo_for(p):
    '''
    ciclo_for : FOR LPAREN m_mark asignacion m_mark condicion_opt PUNTOYCOMA m_mark asignacion m_mark RPAREN LBRACE lista_sentencias_opt RBRACE
    '''
    # Marcadores de posición
    pos_start      = p[3]
    pos_after_init = p[5]
    pos_after_cond = p[8]
    pos_after_incr = p[10]
    pos_end        = len(trip.triplos)

    # Segmentar
    triplos_init = trip.triplos[pos_start:pos_after_init]
    triplos_cond = trip.triplos[pos_after_init:pos_after_cond]
    triplos_incr = trip.triplos[pos_after_cond:pos_after_incr]
    triplos_body = trip.triplos[pos_after_incr:pos_end]

    # Trunca hasta después del init
    trip.rows = trip.rows[:pos_after_init]

    # Condición
    cond = p[6]

    # Etiquetas
    L_begin = trip.new_label("L_for_begin")
    L_end   = trip.new_label("L_for_end")

    # Reensamble: LABEL + cond + IF_FALSE + body + incr + GOTO + LABEL_end
    trip.add('LABEL', arg1=L_begin, res='-')
    trip.insert_triplos(triplos_cond)

    if cond is not None and isinstance(cond, dict) and 'place' in cond:
        trip.add('IF_FALSE_GOTO', arg1=cond['place'], res=L_end)

    trip.insert_triplos(triplos_body)
    trip.insert_triplos(triplos_incr)
    trip.add('GOTO', arg1=L_begin, res='-')
    trip.add('LABEL', arg1=L_end, res='-')

def p_m_mark(p):
    '''
    m_mark : empty
    '''
    p[0] = len(trip.triplos)

def p_condicion_opt(p):
    '''
    condicion_opt : expresion
                  | empty
    '''
    if len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = None

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(p):
    # Podrías registrar errores sintácticos si lo deseas
    # if p is None: trip.error(None, "Fin de entrada inesperado")
    # else: trip.error(str(getattr(p, 'value', '?')), "Token inesperado")
    pass

# ===== Build =====
parser = yacc.yacc(debug=False)
