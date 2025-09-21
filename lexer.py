# lexer.py
import ply.lex as lex

tokens = (
    'ID', 'BADID', 'ENTERO', 'REAL', 'CADENA',   # <-- BADID agregado
    'ASIGNACION',
    'MAS', 'MENOS', 'MULT', 'DIV', 'MOD',
    'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL', 'DIF',
    'AND', 'OR',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMA', 'PUNTOYCOMA',
    'FOR',
    'TIPO',
)

t_ignore = ' \t'

def t_comment_line(t):
    r'//[^\n]*'
    pass

def t_comment_block(t):
    r'/\*[^*]*\*+([^/*][^*]*\*+)*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_TIPO(t):
    r'(cats|cat|meow)\b'
    return t

def t_FOR(t):
    r'for\b'
    return t

# Operadores de 2 chars
t_MAYORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_IGUAL      = r'=='
t_DIF        = r'!='
t_AND        = r'&&'
t_OR         = r'\|\|'

# Operadores de 1 char
t_MAYOR      = r'>'
t_MENOR      = r'<'
t_ASIGNACION = r'='
t_MAS        = r'\+'
t_MENOS      = r'-'
t_MULT       = r'\*'
t_DIV        = r'/'
t_MOD        = r'%'

# Signos y paréntesis
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_COMA       = r','
t_PUNTOYCOMA = r';'

# ---------- Literales ----------
def t_REAL(t):
    r'\d+\.\d+(?![A-Z$])'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'\d+(?![A-Z$])'
    t.value = int(t.value)
    return t

def t_CADENA(t):
    r'"([^\\\n]|(\\.))*?"'
    return t

# ---------- IDs y malas-formaciones ----------
# BADID: casos como 2ITALIA (empieza con dígito y luego mayúsculas/dígitos)
def t_BADID(t):
    r'\d+[A-Z][0-9A-Z]*'
    return t

# ID válido: $ + (dígitos y/o mayúsculas)
def t_ID(t):
    r'\$[0-9A-Z]+'
    return t

def t_error(t):
    # Silenciado: NO registrar errores léxicos
    t.lexer.skip(1)

lexer = lex.lex()
