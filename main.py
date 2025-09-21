# main.py
import tkinter as tk
from tkinter import ttk
from lexer import lexer as lex_inst
from parser import parser
from tables import symbol_table, error_table, lexeme_table

# ---------------- Gutter (números de línea) ----------------
class LineNumbers(tk.Canvas):
    def __init__(self, master, textwidget, **kwargs):
        super().__init__(master, width=48, highlightthickness=0, **kwargs)
        self.textwidget = textwidget

    def redraw(self, *_):
        # Si el Text aún no está listo, reintenta un frame después
        try:
            _ = self.textwidget.dlineinfo("1.0")
        except tk.TclError:
            self.after(16, self.redraw)
            return

        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(44, y, anchor="ne", text=linenum,
                             font=("Consolas", 10), fill="#111827")
            i = self.textwidget.index(f"{i}+1line")

# ---------------- Acciones ----------------
def analizar():
    # Limpiar UI
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)

    # Limpiar modelos
    symbol_table.clear()
    error_table.clear()
    lexeme_table.clear()

    codigo = editor.get("1.0", tk.END)

    # PASO 1: tokenizar para poblar Tabla de lexemas (con tipo en literales)
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    while True:
        tok = lex_inst.token()
        if not tok:
            break

        # OMITIR palabras reservadas que no deben listarse: cat/cats/meow y for
        if tok.type in ("TIPO", "FOR"):
            continue

        # Lexema visible
        lex = tok.value if tok.type == 'CADENA' else str(tok.value)

        # Tipo SOLO para literales
        t = None
        if tok.type == 'CADENA':
            t = 'meow'
        elif tok.type == 'ENTERO':
            t = 'cat'
        elif tok.type == 'REAL':
            t = 'cats'

        lexeme_table.add(lex, t)

    # PASO 2: parsear con el MISMO lexer (reseteado) para llenar símbolos/errores
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    parser.parse(codigo, lexer=lex_inst)

    # PASO 3: completar tipo de IDs declarados en la tabla de lexemas
    for lexema, tipo in symbol_table.rows():
        lexeme_table.set_type_if_id(lexema, tipo)

    # Poblar UI (con zebra)
    for i, (lex, tipo) in enumerate(lexeme_table.rows()):
        tag = "odd" if i % 2 else "even"
        sym_table.insert('', 'end', values=(lex, tipo if tipo else ""), tags=(tag,))

    for i, (token, lexema, renglon, desc) in enumerate(error_table.rows()):
        tag = "odd" if i % 2 else "even"
        err_table.insert('', 'end', values=(token, lexema, renglon, desc), tags=(tag,))

    gutter.redraw()

def limpiar():
    editor.delete("1.0", tk.END)
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    symbol_table.clear()
    error_table.clear()
    lexeme_table.clear()
    lex_inst.lineno = 1
    gutter.redraw()

# ---------------- UI ----------------
root = tk.Tk()
root.title("Compilador U1 - Automatas II (FOR)")
root.geometry("1100x680")

# ----- ESTILOS BONITOS -----
style = ttk.Style(root)
style.theme_use("clam")

style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))

style.configure("Blue.Treeview", font=("Segoe UI", 10), rowheight=26, borderwidth=0)
style.map("Blue.Treeview", background=[("selected", "#cfe8ff")])
style.configure("Blue.Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=6)

# Layout principal
paned = ttk.PanedWindow(root, orient='horizontal')
paned.pack(fill='both', expand=True, padx=8, pady=8)

# ----- Izquierda: editor con gutter -----
left = ttk.Frame(paned)
left.configure(padding=0)
ttk.Label(left, text="Entrada", style="Title.TLabel").pack(anchor='w')

editor_frame = ttk.Frame(left)
editor_frame.pack(fill='both', expand=True, pady=(4,6))

ys = ttk.Scrollbar(editor_frame, orient='vertical')
ys.pack(side='right', fill='y')

# Gutter primero
gutter = LineNumbers(editor_frame, None, bg="#f3f4f6")
gutter.pack(side='left', fill='y')

# Editor
editor = tk.Text(editor_frame, height=25, wrap='none', font=("Consolas", 11), undo=True)
editor.pack(side='left', fill='both', expand=True)
gutter.textwidget = editor

# Sincroniza scroll vertical y repinta números
def _sync_scroll(first, last):
    ys.set(first, last)
    gutter.redraw()
editor.configure(yscrollcommand=_sync_scroll)
ys.config(command=editor.yview)

# Scroll horizontal
xs = ttk.Scrollbar(left, orient='horizontal', command=editor.xview)
editor.configure(xscrollcommand=xs.set)
xs.pack(fill='x')

# Redibuja gutter en cambios/scroll/visibilidad
def _on_any_change(event=None): gutter.redraw()
for seq in ("<KeyRelease>", "<MouseWheel>", "<Button-4>", "<Button-5>",
            "<Configure>", "<Visibility>"):
    editor.bind(seq, _on_any_change)

def _on_modified(event=None):
    editor.edit_modified(False)
    gutter.redraw()
editor.bind("<<Modified>>", _on_modified)

# Timer de seguridad
def _tick():
    gutter.redraw()
    root.after(120, _tick)
root.after(200, _tick)

# Botones
btns = ttk.Frame(left); btns.pack(anchor='e', pady=(2,0))
ttk.Button(btns, text="Analizar", command=analizar).pack(side='left', padx=(0,8))
ttk.Button(btns, text="Limpiar",  command=limpiar).pack(side='left')

paned.add(left, weight=1)

# ----- Derecha: tablas -----
right = ttk.Frame(paned)
paned.add(right, weight=1)

ttk.Label(right, text="Tabla de lexemas", style="Title.TLabel").pack(anchor='w')
sym_table = ttk.Treeview(
    right, columns=("Lexema","Tipo"), show="headings", height=12, style="Blue.Treeview"
)
sym_table.heading("Lexema", text="Lexema")
sym_table.heading("Tipo",   text="Tipo")
sym_table.column("Lexema", width=280, anchor="w", stretch=True)
sym_table.column("Tipo",   width=140, anchor="center")
sym_table.pack(fill='x', pady=(4,10))

ttk.Label(right, text="Tabla de errores", style="Title.TLabel").pack(anchor='w')
err_table = ttk.Treeview(
    right, columns=("Token","Lexema","Renglón","Descripción"),
    show="headings", height=12, style="Blue.Treeview"
)
for col, w, anchor in (
    ("Token", 90, "center"),
    ("Lexema", 220, "w"),
    ("Renglón", 90, "center"),
    ("Descripción", 380, "w"),
):
    err_table.heading(col, text=col)
    err_table.column(col, width=w, anchor=anchor, stretch=(col=="Descripción"))
err_table.pack(fill='both', expand=True, pady=(4,0))

# Zebra rows
sym_table.tag_configure("odd",  background="#f7f7fb")
sym_table.tag_configure("even", background="#ffffff")
err_table.tag_configure("odd",  background="#f7f7fb")
err_table.tag_configure("even", background="#ffffff")

# Atajo para limpiar
root.bind("<Control-l>", lambda e: limpiar())

# Primer repintado del gutter
root.after_idle(gutter.redraw)

root.mainloop()
