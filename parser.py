# parser.py
import ply.yacc as yacc
from lexer import tokens
from tables import symbol_table, error_table

# ---------------------------
# Reglas de precedencia (opcional)
# ---------------------------
precedence = (
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MOD'),
)

# ---------------------------
# Gramática
# ---------------------------

def p_programa(p):
    '''programa : declaraciones
                | declaraciones sentencias'''
    pass

def p_declaraciones(p):
    '''declaraciones : declaraciones declaracion
                     | declaracion'''
    pass

def p_declaracion(p):
    '''declaracion : TIPO ID PUNTOYCOMA'''
    tipo = p[1]
    nombre = p[2]

    # Verificar duplicados
    if symbol_table.exists(nombre):
        error_table.add(None, nombre, p.lineno(2), "Declaración duplicada")
    else:
        symbol_table.add(nombre, tipo)

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    pass

def p_sentencia(p):
    '''sentencia : asignacion
                 | ciclo_for'''
    pass

def p_asignacion(p):
    '''asignacion : ID ASIGNACION expresion PUNTOYCOMA'''
    nombre = p[1]

    # Variable indefinida
    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, p.lineno(1), "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None}
    else:
        tipo_izq = symbol_table.get(nombre)
        tipo_der = p[3]['tipo']

        # Incompatibilidad de tipos
        if tipo_der and tipo_izq and tipo_izq != tipo_der:
            error_table.add(None, nombre, p.lineno(1),
                            f"Incompatibilidad de tipos ({tipo_izq} <- {tipo_der})")

        p[0] = {'lexema': nombre, 'tipo': tipo_izq}

def p_expresion_id(p):
    '''expresion : ID'''
    nombre = p[1]
    if not symbol_table.exists(nombre):
        error_table.add(None, nombre, p.lineno(1), "Variable indefinida")
        p[0] = {'lexema': nombre, 'tipo': None}
    else:
        p[0] = {'lexema': nombre, 'tipo': symbol_table.get(nombre)}

def p_expresion_cadena(p):
    '''expresion : CADENA'''
    p[0] = {'lexema': p[1], 'tipo': 'meow'}  # cadenas = tipo meow

def p_expresion_entero(p):
    '''expresion : ENTERO'''
    p[0] = {'lexema': str(p[1]), 'tipo': 'cat'}  # enteros = tipo cat

def p_expresion_real(p):
    '''expresion : REAL'''
    p[0] = {'lexema': str(p[1]), 'tipo': 'cats'}  # reales = tipo cats

def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MOD expresion'''
    tipo_izq = p[1]['tipo']
    tipo_der = p[3]['tipo']

    if tipo_izq and tipo_der and tipo_izq != tipo_der:
        # Ahora reportamos el identificador izquierdo, no el operador
        error_table.add(None, p[1]['lexema'], p.lineno(1),
                        f"Incompatibilidad de tipos ({tipo_izq} <- {tipo_der})")

    p[0] = {'lexema': p[1]['lexema'], 'tipo': tipo_izq or tipo_der}

def p_ciclo_for(p):
    '''ciclo_for : FOR LPAREN asignacion PUNTOYCOMA expresion PUNTOYCOMA asignacion RPAREN LBRACE sentencias RBRACE'''
    pass

def p_error(p):
    # ⚠️ No reportamos errores sintácticos, solo semánticos
    pass

# ---------------------------
# Parser
# ---------------------------
parser = yacc.yacc()
