import ply.yacc as yacc
from lexer import tokens
from tables import SymbolTable, ErrorTable

symbol_table = SymbolTable()
error_table = ErrorTable()

# ---------- utilidades ----------
def tipo_de_valor(val):
    if isinstance(val, int):   return 'cat'
    if isinstance(val, float): return 'cats'
    if isinstance(val, str) and val.startswith('"') and val.endswith('"'):
        return 'meow'
    return None

def compatibles(tipo_destino, tipo_origen):
    if tipo_destino == 'cat':
        return tipo_origen == 'cat'
    if tipo_destino == 'cats':
        return tipo_origen in ('cat', 'cats')
    if tipo_destino == 'meow':
        return tipo_origen == 'meow'
    return True

# ---------- gramática ----------
def p_programa(p):
    '''programa : programa sentencia
                | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | ciclo_for'''
    pass

# TIPO ID ;
def p_declaracion(p):
    'declaracion : TIPO ID PUNTOYCOMA'
    lexema = p[2]
    tipo   = p[1]
    if symbol_table.exists(lexema):
        error_table.add(None, lexema, p.lineno(2), "Declaración duplicada")
    else:
        symbol_table.add(lexema, tipo)

# ID = expresion ;
def p_asignacion(p):
    'asignacion : ID ASIGNACION expresion PUNTOYCOMA'
    destino = p[1]
    if not symbol_table.exists(destino):
        error_table.add(None, destino, p.lineno(1), "Variable indefinida")
        return
    tipo_destino = symbol_table.get(destino)
    tipo_origen  = p[3]['tipo']
    if not compatibles(tipo_destino, tipo_origen):
        error_table.add(None, destino, p.lineno(1), f"Incompatibilidad de tipos ({tipo_destino} <- {tipo_origen})")

# Asignación SIN ';' (para el incremento del for)
def p_asignacion_simple(p):
    'asignacion_simple : ID ASIGNACION expresion'
    destino = p[1]
    if not symbol_table.exists(destino):
        error_table.add(None, destino, p.lineno(1), "Variable indefinida")
        p[0] = {'tipo': 'cat'}
        return
    tipo_destino = symbol_table.get(destino)
    tipo_origen  = p[3]['tipo']
    if not compatibles(tipo_destino, tipo_origen):
        error_table.add(None, destino, p.lineno(1), f"Incompatibilidad de tipos ({tipo_destino} <- {tipo_origen})")
    p[0] = {'tipo': tipo_destino}

# for ( asignacion condicion ; asignacion_simple ) { cuerpo }
def p_ciclo_for(p):
    'ciclo_for : FOR LPAREN asignacion condicion PUNTOYCOMA asignacion_simple RPAREN LBRACE cuerpo RBRACE'
    pass

def p_condicion(p):
    'condicion : expresion_rel'
    p[0] = p[1]

def p_expresion_rel(p):
    '''expresion_rel : expresion MAYOR expresion
                     | expresion MENOR expresion
                     | expresion MAYORIGUAL expresion
                     | expresion MENORIGUAL expresion
                     | expresion IGUAL expresion
                     | expresion DIF expresion'''
    p[0] = {'tipo': 'cat'}  # no forzamos booleanos en esta unidad

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MOD expresion'''
    t1, t2 = p[1]['tipo'], p[3]['tipo']
    if 'meow' in (t1, t2):
        p[0] = {'tipo': 'meow'}
    elif 'cats' in (t1, t2):
        p[0] = {'tipo': 'cats'}
    else:
        p[0] = {'tipo': 'cat'}

def p_expresion_group(p):
    'expresion : LPAREN expresion RPAREN'
    p[0] = p[2]

def p_expresion_id(p):
    'expresion : ID'
    lexema = p[1]
    if not symbol_table.exists(lexema):
        error_table.add(None, lexema, p.lineno(1), "Variable indefinida")
        p[0] = {'tipo': 'cat'}
    else:
        p[0] = {'tipo': symbol_table.get(lexema)}

def p_expresion_num(p):
    '''expresion : ENTERO
                 | REAL'''
    p[0] = {'tipo': tipo_de_valor(p[1])}

def p_expresion_cadena(p):
    'expresion : CADENA'
    p[0] = {'tipo': 'meow'}

def p_cuerpo(p):
    '''cuerpo : cuerpo sentencia
              | sentencia
              | empty'''
    pass

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        # Token y lexema del símbolo problemático
        error_table.add(None, str(p.value), p.lineno, "Error de sintaxis")
    else:
        error_table.add(None, "EOF", 0, "Error de sintaxis al final del archivo")

parser = yacc.yacc(start='programa')
