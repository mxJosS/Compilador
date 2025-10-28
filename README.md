<h1>Compilador U1, U2 – Lenguajes y Autómatas II (FOR)</h1>
<p>
  Mini–compilador didáctico en <b>Python + PLY (lex/yacc)</b> y <b>Tkinter</b> que simula
  análisis léxico, sintáctico y semántico. Incluye GUI con editor (izquierda) y tablas
  de símbolos/errores (derecha).
</p>

<p>
  <sub>Tipos: <code>cat</code>, <code>cats</code>, <code>meow</code> · Identificadores (ER): <code>[0-9A-Z]+</code> · Estructura: <code>for</code></sub>
</p>

<hr/>

<h2>Características</h2>

<ul>
  <li>GUI con Tkinter: editor de código + <b>Tabla de símbolos</b> (Lexema, Tipo) y <b>Tabla de errores</b> (Token ES#, Lexema, Renglón, Descripción).</li>
  <li>Soporta: declaraciones, asignaciones, expresiones aritméticas/relacionales e instrucción <code>for</code>.</li>
  <li>Chequeos semánticos: <i>declaración duplicada</i>, <i>variable indefinida</i>, <i>incompatibilidad de tipos</i>.</li>
</ul>

<h2>Tecnologías</h2>
<ul>
  <li>Python 3.10+</li>
  <li>PLY 3.11</li>
  <li>Tkinter</li>
</ul>

<h2>Estructura</h2>

<pre><code>Compilador/
├─ lexer.py          # Tokens, ER y reservadas (cat/cats/meow, for)
├─ parser.py         # Gramática + 'for' + semántica (ES#)
├─ tables.py         # Modelos Tabla de símbolos / Tabla de errores
├─ main.py           # GUI (editor izquierda, tablas derecha)
├─ ejecutar.bat      # Ejecuta la app (activa venv y corre main.py)
└─ instalar_dependencias.bat  # Crea venv e instala librerías
</code></pre>

<h2>Lenguaje</h2>

<table>
  <tr><th>Elemento</th><th>Descripción</th></tr>
  <tr><td>Tipos</td><td><code>cat</code> (entero), <code>cats</code> (real/entero), <code>meow</code> (cadena)</td></tr>
  <tr><td>Identificadores</td><td>Exp. regular <code>[0-9A-Z]+</code> (ej. <code>ITA1</code>, <code>ABC123</code>)</td></tr>
  <tr><td>Reservadas</td><td><code>for</code></td></tr>
  <tr><td>Operadores</td><td><code>+ - * / %</code>, <code>&gt; &lt; &gt;= &lt;= == !=</code> (lógicos definidos: <code>&amp;&amp;</code>, <code>||</code>)</td></tr>
  <tr><td>Formas</td><td>
    Declaración: <code>TIPO ID ;</code><br/>
    Asignación: <code>ID = expresion ;</code><br/>
    For: <code>for ( asignacion ; condicion ; asignacion_simple ) { cuerpo }</code><br/>
    <small><i>(Incremento sin <code>;</code> para no chocar con <code>)</code>)</i></small>
  </td></tr>
</table>

<h2>Ejecutar en Windows</h2>

<ol>
  <li><b>Instalar dependencias (una vez)</b><br/>
    <code>.\instalar_dependencias.bat</code>
  </li>
  <li><b>Ejecutar la app</b><br/>
    <code>.\ejecutar.bat</code>
  </li>
</ol>

<p>
  Atajo: <kbd>Ctrl</kbd> + <kbd>L</kbd> limpia editor y tablas.
</p>

<h2>Ejemplos</h2>

<details>
  <summary><b>✅ Caso sin errores</b></summary>
  <pre><code>cat ITA1;
cats ITA2;
meow ITA3;

ITA1 = 0;
ITA2 = 5;

for (ITA1 = 0; ITA1 &lt; 3; ITA1 = ITA1 + 1) {
    ITA2 = ITA2 + ITA1;
    ITA3 = "hola";
}
</code></pre>
</details>

<details>
  <summary><b>❌ Caso con errores (semánticos)</b></summary>
  <pre><code>cat ITA1;
cat ITA1;            // duplicada
cats ITA2;

ITA4 = 10;           // indefinida
ITA2 = "hola";       // incompatibilidad (cats &lt;- meow)

for (ITA1 = 0; ITA1 &lt; 2; ITA1 = ITA1 + 1) {
    ITA5 = ITA5 + 1; // indefinida
    ITA3 = ITA3 + 1; // incompatibilidad (meow &lt;- cat)
}
</code></pre>
</details>

<h2>Solución de problemas</h2>

<ul>
  <li><b>“Carácter ilegal 'c'…”</b> — En <code>lexer.py</code> asegúrate:
    <pre><code>def t_TIPO(t): r'(cats|cat|meow)\b'; return t
def t_FOR(t):  r'for\b'; return t
def t_ID(t):   r'[0-9A-Z]+'; return t
</code></pre>
  </li>
  <li><b>Errores con for</b> — El incremento NO lleva <code>;</code>:
    <pre><code>for (ITA1 = 0; ITA1 &lt; 3; ITA1 = ITA1 + 1) { ... }</code></pre>
  </li>
  <li><b>No toma cambios de la gramática</b> — Borra <code>parsetab.py</code> y vuelve a ejecutar.</li>
</ul>

<h2>(Opcional) Generar .exe</h2>
<pre><code>pip install pyinstaller
pyinstaller --onefile --windowed main.py
</code></pre>
<p>Salida: <code>dist/main.exe</code></p>

<hr/>

<p><sub>Desarrollado por Jose Angel Espinosa & Endrick Pinzón Peña · Materia: Lenguajes y Autómatas II – Unidad 1 (Análisis Semántico)</sub></p>
