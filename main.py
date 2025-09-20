import tkinter as tk
from tkinter import ttk
from parser import parser, symbol_table, error_table
from lexer import lexer as lex_inst
from tables import LexemeTable

# ---------------- Gutter: números de línea ----------------
class LineNumbers(tk.Canvas):
    def __init__(self, master, textwidget=None, **kwargs):
        super().__init__(master, width=48, highlightthickness=0, **kwargs)
        self.textwidget = textwidget

    def redraw(self, *args):
        self.delete("all")
        if not self.textwidget:
            return
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(44, y, anchor="ne", text=linenum, font=("Consolas", 10))
            i = self.textwidget.index(f"{i}+1line")

# ---------------- Modelo: tabla de lexemas ----------------
lexeme_table = LexemeTable()

# ---------------- Acciones ----------------
def analizar():
    # Limpiar tablas UI
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    # Limpiar modelos
    symbol_table.clear()
    error_table.clear()
    lexeme_table.clear()

    codigo = editor.get("1.0", tk.END)

    # PASO 1: pre-scan léxico para llenar Tabla de lexemas
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    while True:
        tok = lex_inst.token()
        if not tok:
            break
        lex = tok.value if tok.type == 'CADENA' else str(tok.value)
        lexeme_table.add(lex)

    # PASO 2: parsear (reinyectamos y reiniciamos líneas)
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    parser.parse(codigo, lexer=lex_inst)

    # PASO 3: completar tipo de IDs declarados
    for lexema, tipo in symbol_table.rows():
        lexeme_table.set_type_if_id(lexema, tipo)

    # Poblar Tabla de lexemas (Lexema, Tipo)
    for lex, tipo in lexeme_table.rows():
        sym_table.insert('', 'end', values=(lex, tipo if tipo else ""))

    # Poblar Tabla de errores
    for token, lexema, renglon, desc in error_table.rows():
        err_table.insert('', 'end', values=(token, lexema, renglon, desc))

    gutter.redraw()

def limpiar():
    editor.delete("1.0", tk.END)
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    symbol_table.clear()
    error_table.clear()
    lex_inst.lineno = 1
    gutter.redraw()

# ---------------- UI ----------------
root = tk.Tk()
root.title("Compilador U1 - Automatas II (FOR)")
root.geometry("1100x700")

# Estilos
style = ttk.Style(root)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Blue.Treeview", font=("Segoe UI", 11), rowheight=28)
style.map("Treeview", background=[('selected', '#cfe8ff')])

# Layout principal
paned = ttk.PanedWindow(root, orient='horizontal')
paned.pack(fill='both', expand=True, padx=8, pady=8)

# ---- Izquierda: Editor con gutter ----
left = ttk.Frame(paned)
ttk.Label(left, text="Entrada", font=("Segoe UI", 11, "bold")).pack(anchor='w')

editor_frame = ttk.Frame(left)
editor_frame.pack(fill='both', expand=True, pady=(4,6))

# Scroll vertical
yscroll = ttk.Scrollbar(editor_frame, orient='vertical')
yscroll.pack(side='right', fill='y')

# Gutter primero (izquierda)
gutter = LineNumbers(editor_frame, None, bg="#f3f4f6")
gutter.pack(side='left', fill='y')

# Editor
editor = tk.Text(editor_frame, height=25, wrap='none', font=("Consolas", 11), undo=True)
editor.pack(side='left', fill='both', expand=True)

gutter.textwidget = editor

def _yscroll_proxy(*args):
    yscroll.set(*args)
    gutter.redraw()
editor.configure(yscrollcommand=_yscroll_proxy)
yscroll.config(command=editor.yview)

# Scroll horizontal
xscroll = ttk.Scrollbar(left, orient='horizontal', command=editor.xview)
editor.configure(xscrollcommand=xscroll.set)
xscroll.pack(fill='x')

# Redibujos del gutter
def _on_modified(event=None):
    editor.edit_modified(False)
    gutter.redraw()
editor.edit_modified(False)
editor.bind('<<Modified>>', _on_modified)
editor.bind('<KeyRelease>',      lambda e: gutter.redraw())
editor.bind('<ButtonRelease-1>', lambda e: gutter.redraw())
editor.bind('<MouseWheel>',      lambda e: gutter.redraw())   # Windows
editor.bind('<Button-4>',        lambda e: gutter.redraw())   # Linux up
editor.bind('<Button-5>',        lambda e: gutter.redraw())   # Linux down
editor.bind('<Configure>',       lambda e: gutter.redraw())

# Botones
btns = ttk.Frame(left)
btns.pack(anchor='e', pady=(2,0))
ttk.Button(btns, text="Analizar", command=analizar).pack(side='left', padx=(0,8))
ttk.Button(btns, text="Limpiar",  command=limpiar).pack(side='left')

paned.add(left, weight=1)

# ---- Derecha: Tablas ----
right = ttk.Frame(paned)
paned.add(right, weight=1)

# Tabla de lexemas (Lexema / Tipo) — centradas
ttk.Label(right, text="Tabla de lexemas", font=("Segoe UI", 11, "bold")).pack(anchor='w')
sym_table = ttk.Treeview(
    right, columns=("Lexema","Tipo"), show="headings", height=12, style="Blue.Treeview"
)
sym_table.heading("Lexema", text="Lexema", anchor='center')
sym_table.heading("Tipo",   text="Tipo",   anchor='center')
sym_table.column("Lexema", width=300, anchor='center', stretch=True)
sym_table.column("Tipo",   width=180, anchor='center', stretch=True)
sym_table.pack(fill='x', pady=(4,10))

# Tabla de errores — centradas y con scrolls
ttk.Label(right, text="Tabla de errores", font=("Segoe UI", 11, "bold")).pack(anchor='w')

err_wrap = ttk.Frame(right)
err_wrap.pack(fill='both', expand=True, pady=(4,0))

err_table = ttk.Treeview(
    err_wrap,
    columns=("Token","Lexema","Renglón","Descripción"),
    show="headings",
    height=12,
    style="Blue.Treeview"
)
err_table["displaycolumns"] = ("Token","Lexema","Renglón","Descripción")

err_table.heading("Token",       text="Token",       anchor='center')
err_table.heading("Lexema",      text="Lexema",      anchor='center')
err_table.heading("Renglón",     text="Renglón",     anchor='center')
err_table.heading("Descripción", text="Descripción", anchor='center')

err_table.column("Token",       width=120, anchor='center', stretch=True)
err_table.column("Lexema",      width=260, anchor='center', stretch=True)
err_table.column("Renglón",     width=110, anchor='center', stretch=True)
err_table.column("Descripción", width=420, anchor='center', stretch=True)

yerr = ttk.Scrollbar(err_wrap, orient='vertical',   command=err_table.yview)
xerr = ttk.Scrollbar(err_wrap, orient='horizontal', command=err_table.xview)
err_table.configure(yscrollcommand=yerr.set, xscrollcommand=xerr.set)

err_table.grid(row=0, column=0, sticky="nsew")
yerr.grid(row=0, column=1, sticky="ns")
xerr.grid(row=1, column=0, sticky="ew")
err_wrap.rowconfigure(0, weight=1)
err_wrap.columnconfigure(0, weight=1)

# Atajo para limpiar
root.bind("<Control-l>", lambda e: limpiar())

# Primer pintado del gutter
root.after(30, gutter.redraw)

root.mainloop()
