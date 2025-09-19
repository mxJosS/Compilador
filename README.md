Compilador U1 – Lenguajes y Autómatas II (FOR)

Pequeño compilador didáctico con PLY (lex/yacc) y Tkinter que simula las fases básicas (léxico, sintáctico y semántico) de un lenguaje mini con:

Tipos de dato: cat, cats, meow

Identificadores (ER): [0-9A-Z]+ (solo MAYÚSCULAS y dígitos; p. ej. ITA1, VAR123)

Estructuras soportadas: declaraciones, asignaciones, expresiones aritméticas y relacionales, e instrucción for

La app muestra una GUI donde escribes el código a la izquierda y, a la derecha, se visualizan las tablas:

Tabla de símbolos (Lexema, Tipo)

Tabla de errores (Token ES#, Lexema, Renglón, Descripción)

⚙️ Tecnologías

Python 3.10+

PLY 3.11 (análisis léxico y sintáctico)

Tkinter (interfaz gráfica)

(Opcional) emoji para mensajes

📁 Estructura del proyecto
Compilador/
├─ lexer.py          # Analizador léxico (tokens, ER, reservadas)
├─ parser.py         # Parser + chequeos semánticos + gramática del 'for'
├─ tables.py         # Modelos de Tabla de símbolos y Tabla de errores (ES#)
├─ main.py           # GUI con Tkinter (editor izquierda, tablas derecha)
├─ ejecutar.bat      # Ejecuta la app (activa venv y corre main.py)
└─ instalar_dependencias.bat  # Crea venv e instala librerías

🧠 Especificación del lenguaje

Tipos (palabras reservadas, minúsculas):

cat → enteros

cats → reales (acepta entero o real)

meow → cadenas

Identificadores:

ER: [0-9A-Z]+ (ej.: ITA1, ABC123)

Palabras reservadas:

for

Operadores:

Aritméticos: + - * / %

Relacionales: > < >= <= == !=

Lógicos (tokens definidos; uso opcional): && ||

Estructuras:

Declaración: TIPO ID ;

Asignación: ID = expresion ;

for ( asignacion ; condicion ; asignacion_simple ) { cuerpo }

Nota: el incremento es una asignación sin ; para no chocar con el ).

Semántica:

Declaración duplicada

Variable indefinida

Incompatibilidad de tipos (p. ej., meow <- cat)

Los errores se listan como ES1, ES2, … (únicos), y no se repite la combinación (Lexema, Renglón).

🖥️ Ejecutar (Windows)
1) Instalar dependencias (una sola vez)

Doble clic a instalar_dependencias.bat
o desde PowerShell/CMD:

.\instalar_dependencias.bat


Crea venv\ e instala ply, tk, emoji y actualiza pip.

2) Ejecutar la app

Doble clic a ejecutar.bat
o desde PowerShell/CMD:

.\ejecutar.bat


Activa el venv y corre python main.py.
