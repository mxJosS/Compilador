# parser.py
import ply.yacc as yacc
from lexer import tokens        # usa los mismos tokens del lexer
from tables import SymbolTable, ErrorTable

# Instancias compartidas (importadas por main.py)
symbol_table = SymbolTable()
error_table  = ErrorTable()

# -------------------------------------------------------
# Utilidades de tipos
# -------------------------------------------------------

def tipo_resultante_num(t1, t2):
    """
    Resultado de una operación numérica/binaria:
    - si alguno es meow -> meow
    - si alguno es cats -> cats
    - si ambos cat -> cat
    """
    if 'meow' in (t1, t2):
        return 'meow'
    if 'cats' in (t1, t2):
        return 'cats'
    return 'cat'

def compatible(dst, src):
    """
    ¿src puede asignarse a dst?
    - meow solo con meow
    - cat -> cats permitido (promoción)
    - cats -> cat NO permitido
    - cat <-> cat permitido; cats <-> cats permitido
    - cualquier numérico -> meow NO permitido y viceversa
    """
    if dst == 'meow' and src == 'meow':
        return True
    if dst == 'meow' and src != 'meow':
        return False
    if dst != 'meow' and src == 'meow':
        return False
    # ambos numéricos
    if dst == 'cats' and src in ('cat', 'cats'):
        return True
    if dst == 'cat' and src == 'cat':
        return True
    # cats -> cat
    return False

# -------------------------------------------------------
# Precedencia (reduce conflictos)
# -------------------------------------------------------
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL', 'DIF'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('right', 'UMINUS', 'UPLUS'),
)

# -------------------------------------------------------
# Gramática
# -------------------------------------------------------

def p_programa(p):
    'programa : lista_sentencias_opt'
    p[0] = None

def p_lista_sentencias_opt(p):
    '''lista_sentencias_opt : lista_sentencias
                            | empty'''
    p[0] = None

def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia
                        | sentencia'''
    p[0] = None

def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | ciclo_for
                 | expresion PUNTOYCOMA'''
    # La sentencia de expresión permite líneas como:  ID + ID ;
    p[0] = None

# ---------------- Declaraciones ----------------

def p_declaracion(p):
    'declaracion : TIPO ID PUNTOYCOMA'
    tipo = p[1]       # 'cat' | 'cats' | 'meow' (viene del lexer)
    lex  = p[2]

    if symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(2), "Declaración duplicada")
    else:
        symbol_table.add(lex, tipo)

# ---------------- Asignaciones -----------------

def p_asignacion(p):
    'asignacion : ID ASIGNACION expresion PUNTOYCOMA'
    lex  = p[1]
    texp = p[3]['tipo']

    if not symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(1), "Variable indefinida")
        return

    tvar = symbol_table.get(lex)
    if not compatible(tvar, texp):
        error_table.add(None, lex, p.lineno(1), f"Incompatibilidad de tipos ({tvar} <- {texp})")

def p_asignacion_simple(p):
    'asignacion_simple : ID ASIGNACION expresion'
    # igual que asignacion pero SIN ';' (se usa en el incremento del for)
    lex  = p[1]
    texp = p[3]['tipo']

    if not symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(1), "Variable indefinida")
        return

    tvar = symbol_table.get(lex)
    if not compatible(tvar, texp):
        error_table.add(None, lex, p.lineno(1), f"Incompatibilidad de tipos ({tvar} <- {texp})")

# ---------------- For --------------------------

def p_ciclo_for(p):
    'ciclo_for : FOR LPAREN asignacion condicion PUNTOYCOMA asignacion_simple RPAREN LBRACE cuerpo RBRACE'
    p[0] = None

def p_cuerpo(p):
    '''cuerpo : lista_sentencias_opt'''
    p[0] = None

# Puedes hacer que condicion sea una expresion relacional u OR/AND de ellas.
def p_condicion(p):
    '''condicion : expresion_rel
                 | expresion_rel OR expresion_rel
                 | expresion_rel AND expresion_rel'''
    # semánticamente la condición produce algo "booleano", lo mapeamos a 'cat'
    p[0] = {'tipo': 'cat'}

# ---------------- Expresiones ------------------

def p_expresion_paren(p):
    'expresion : LPAREN expresion RPAREN'
    p[0] = p[2]

def p_expresion_id(p):
    'expresion : ID'
    lex = p[1]
    if not symbol_table.exists(lex):
        error_table.add(None, lex, p.lineno(1), "Variable indefinida")
        p[0] = {'tipo': 'cat'}  # por defecto para continuar
    else:
        p[0] = {'tipo': symbol_table.get(lex)}

def p_expresion_entero(p):
    'expresion : ENTERO'
    p[0] = {'tipo': 'cat'}

def p_expresion_real(p):
    'expresion : REAL'
    p[0] = {'tipo': 'cats'}

def p_expresion_cadena(p):
    'expresion : CADENA'
    p[0] = {'tipo': 'meow'}

def p_expresion_unaria(p):
    '''expresion : MENOS expresion %prec UMINUS
                 | MAS expresion %prec UPLUS'''
    t = p[2]['tipo']
    # Si llega meow, lo propagamos como meow; lo numérico se normaliza a cat/cats
    p[0] = {'tipo': ('meow' if t == 'meow' else ('cats' if t == 'cats' else 'cat'))}

def p_expresion_binaria_arit(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion MOD expresion'''
    t1, t2 = p[1]['tipo'], p[3]['tipo']
    p[0] = {'tipo': tipo_resultante_num(t1, t2)}

def p_expresion_rel(p):
    '''expresion_rel : expresion MAYOR expresion
                     | expresion MENOR expresion
                     | expresion MAYORIGUAL expresion
                     | expresion MENORIGUAL expresion
                     | expresion IGUAL expresion
                     | expresion DIF expresion'''
    # el resultado lógico lo representamos como 'cat' (entero 0/1)
    p[0] = {'tipo': 'cat'}

# ---------------- Utilidades -------------------

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        # Guardamos el lexema problemático y su línea
        error_table.add(None, str(p.value), p.lineno, "Error de sintaxis")
        # Recuperación simple: descartar token y continuar
        yacc.yacc().errok()
    else:
        # EOF inesperado
        error_table.add(None, "EOF", 0, "Error de sintaxis al final del archivo")

# -------------------------------------------------------
# Constructor del parser
# -------------------------------------------------------
parser = yacc.yacc()
