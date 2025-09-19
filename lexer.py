import ply.lex as lex

tokens = (
    'ID', 'ENTERO', 'REAL', 'CADENA',
    'ASIGNACION',
    'MAS', 'MENOS', 'MULT', 'DIV', 'MOD',
    'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL', 'DIF',
    'AND', 'OR',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMA', 'PUNTOYCOMA',
    'FOR',
    'TIPO',
)

# Ignorar espacios/tabs y comentarios tipo //
t_ignore = ' \t'
def t_comment_line(t):
    r'//[^\n]*'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Palabras reservadas en minúscula ---
# ¡OJO! El orden importa: 'cats' antes que 'cat', y con \b (límite de palabra)
def t_TIPO(t):
    r'(cats|cat|meow)\b'
    return t

def t_FOR(t):
    r'for\b'
    return t

# Operadores de 2 chars primero
t_MAYORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_IGUAL      = r'=='
t_DIF        = r'!='
t_AND        = r'&&'
t_OR         = r'\|\|'

# Operadores 1 char
t_MAYOR      = r'>'
t_MENOR      = r'<'
t_ASIGNACION = r'='
t_MAS        = r'\+'
t_MENOS      = r'-'
t_MULT       = r'\*'
t_DIV        = r'/'
t_MOD        = r'%'

# Paréntesis y signos
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACE     = r'\{'
t_RBRACE     = r'\}'
t_COMA       = r','
t_PUNTOYCOMA = r';'

# Literales
def t_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CADENA(t):
    r'"([^\\\n]|(\\.))*?"'
    return t

# Tu ER de identificadores: SOLO MAYÚSCULAS y DÍGITOS
def t_ID(t):
    r'[0-9A-Z]+'
    return t

def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
