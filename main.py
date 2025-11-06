import tkinter as tk
from tkinter import ttk
from lexer import lexer as lex_inst
from parser import parser
from tables import symbol_table, error_table, lexeme_table
from triplos_ui import get_triplos_table, reset_triplos_table  # reset triplos

# ---------------- Gutter (números de línea) ----------------
class LineNumbers(tk.Canvas):
    def __init__(self, master, textwidget, **kwargs):
        super().__init__(master, width=48, highlightthickness=0, **kwargs)
        self.textwidget = textwidget

    def redraw(self, *_):
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

# ---------------- Util: OP visual + explicación ----------------
def _display_op(op: str, do: str = "") -> str:
    """Convierte mnemónicos del backend a símbolos/etiquetas amigables para la UI."""
    mapa = {
        'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/', 'MOD': '%',
        'AND': '&&', 'OR': '||', 'NOT': '!',
        ':=': '=',
        'GT': '>', 'GTE': '>=', 'LT': '<', 'LTE': '<=', 'EQ': '==', 'NEQ': '!='
    }
    if op in mapa:
        return mapa[op]

    # Presentación limpia de LABEL/GOTO de los for
    if op == "LABEL" and (do or "").startswith("L_for_begin"):
        return "BEGIN"
    if op == "LABEL" and (do or "").startswith("L_for_end"):
        return "END"
    if op == "GOTO" and (do or "").startswith("L_for_begin"):
        return "JUMP → BEGIN"
    if op == "GOTO" and (do or "").startswith("L_for_end"):
        return "JUMP → END"

    return op

def _pretty_label(alias: str) -> str:
    """Convierte nombres de etiqueta a alias legibles."""
    if not alias:
        return ""
    if alias.startswith("L_for_begin"):
        return "BEGIN"
    if alias.startswith("L_for_end"):
        return "END"
    return alias

def _explain_op(op: str) -> str:
    if op in {"+","-","*","/","%"}: return f"Operación aritmética ({op})"
    if op in {"&&","||","!"}:        return f"Operación lógica ({op})"
    if op in {"==","!=", "<","<=",">",">="}: return f"Comparación ({op})"
    if op == "=":                    return "Asignación (=)"
    if op in {"JMP","GOTO"}:         return "Salto incondicional"
    if op in {"IF","IF_FALSE_GOTO","IF NOT"}:
        return "Si NO(condición) salta a la etiqueta"
    if op == "LABEL":                return "Etiqueta (marca de salto)"
    if op == "BEGIN":                return "Inicio de bucle (LABEL)"
    if op == "END":                  return "Fin de bucle (LABEL)"
    if op == "JUMP → BEGIN":         return "Salto al inicio del bucle"
    if op == "JUMP → END":           return "Salto al fin del bucle"
    if op == "TRUE":                 return "Bandera TRUE (visual)"
    if op == "FALSE":                return "Bandera FALSE (visual)"
    if op == "LIT":                  return "Literal (valor constante)"
    if op == "REF":                  return "Referencia a variable"
    if op == "ERROR":                return "Error detectado (ver tabla de errores)"
    return "—"

# --- Filas TRUE/FALSE virtuales (solo presentación, no backend) ---
_COMPARISON_MNEMONICS = {"GT","GTE","LT","LTE","EQ","NEQ"}  # lo que emite tu parser

def _augment_truth_rows(rows):
    """
    Inserta filas visuales con OP=TRUE y OP=FALSE después de cada comparación.
    rows: lista de dicts con claves "#","OP","DO","DF"
    """
    out = []
    for r in rows:
        out.append(r)
        op = r.get("OP", "")
        if op in _COMPARISON_MNEMONICS:
            temp = r.get("DO", "")  # el temporal resultado de la comparación
            out.append({"#": "", "OP": "TRUE",  "DO": temp, "DF": ""})
            out.append({"#": "", "OP": "FALSE", "DO": temp, "DF": ""})
    return out

# ---------------- Acciones ----------------
def analizar():
    # Limpiar UI
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    for w in tri_table.get_children(): tri_table.delete(w)

    # Limpiar modelos
    symbol_table.clear()
    error_table.clear()
    lexeme_table.clear()
    reset_triplos_table()     # limpia triplos y resetea #, temps, etc.

    codigo = editor.get("1.0", tk.END)

    # PASO 1: tokenizar (Tabla de lexemas)
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    while True:
        tok = lex_inst.token()
        if not tok:
            break

        # OMITIR palabras reservadas: cat/cats/meow y for
        if tok.type in ("TIPO", "FOR"):
            continue

        lex = tok.value if tok.type == 'CADENA' else str(tok.value)

        t = None
        if tok.type == 'CADENA':
            t = 'meow'
        elif tok.type == 'ENTERO':
            t = 'cat'
        elif tok.type == 'REAL':
            t = 'cats'

        lexeme_table.add(lex, t)

    # PASO 2: parsear (símbolos/errores + triplos)
    lex_inst.lineno = 1
    lex_inst.input(codigo)
    parser.parse(codigo, lexer=lex_inst)

    # PASO 3: completar tipo de IDs en la tabla de lexemas
    for lexema, tipo in symbol_table.rows():
        lexeme_table.set_type_if_id(lexema, tipo)

    # Poblar UI - Lexemas
    for i, (lex, tipo) in enumerate(lexeme_table.rows()):
        tag = "odd" if i % 2 else "even"
        sym_table.insert('', 'end', values=(lex, tipo if tipo else ""), tags=(tag,))

    # Poblar UI - Errores
    for i, (token, lexema, renglon, desc) in enumerate(error_table.rows()):
        tag = "odd" if i % 2 else "even"
        err_table.insert('', 'end', values=(token, lexema, renglon, desc), tags=(tag,))

    # Poblar UI - Triplos
    tri_data = get_triplos_table()
    # Forzamos los headers base para evitar desincronización
    tri_headers = ["#", "OP", "DO", "DF"]
    tri_headers_ui = ("#", "OP", "DO", "DF", "Explicación")

    # Inyectar TRUE/FALSE visuales tras comparaciones
    base_rows = _augment_truth_rows(tri_data["rows"])

    for i, row in enumerate(base_rows):
        tag = "odd" if i % 2 else "even"

        op_raw  = row.get('OP', '')
        do_val  = row.get('DO', '')
        op_disp = _display_op(op_raw, do_val)

        # Clon para no mutar datos reales
        row_disp = dict(row)
        row_disp['OP'] = op_disp

        # Presentación bonita de IF_FALSE_GOTO: IF NOT | cond | JUMP → ALIAS
        if op_raw == "IF_FALSE_GOTO":
            label_raw = row.get('DO', '')
            cond_raw  = row.get('DF', '')
            label_nice = _pretty_label(label_raw)
            row_disp['OP'] = "IF NOT"
            row_disp['DO'] = cond_raw or ''
            row_disp['DF'] = f"JUMP → {label_nice}" if label_nice else "JUMP"

        # Para BEGIN/END/JUMP ocultamos DO/DF (solo presentación)
        if row_disp['OP'] in {"BEGIN", "END", "JUMP → BEGIN", "JUMP → END"}:
            row_disp['DO'] = ""
            row_disp['DF'] = ""

        # Guion visual si DO/DF vacíos (solo UI)
        if row_disp.get('DF', '') == '':
            row_disp['DF'] = '—'
        if row_disp.get('DO', '') == '':
            row_disp['DO'] = '—'

        # <<< Renumeración UI: # consecutivo en orden visual >>>
        row_disp['#'] = str(i + 1)

        exp = _explain_op(row_disp['OP'])
        values = [row_disp.get(h, "") for h in tri_headers] + [exp]

        # Tag visual suave para filas BEGIN/END/JUMP/TRUE/FALSE/IF NOT
        ghost = row_disp['OP'] in {"BEGIN","END","JUMP → BEGIN","JUMP → END","TRUE","FALSE","IF NOT"}
        tags = (tag, "ghost") if ghost else (tag,)
        tri_table.insert('', 'end', values=values, tags=tags)

    gutter.redraw()

def limpiar():
    editor.delete("1.0", tk.END)
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    for w in tri_table.get_children(): tri_table.delete(w)
    symbol_table.clear()
    error_table.clear()
    lexeme_table.clear()
    reset_triplos_table()
    lex_inst.lineno = 1
    gutter.redraw()

# ---------------- UI ----------------
root = tk.Tk()
root.title("Compilador U1 - Automatas II (FOR)")
root.geometry("1200x820")

# ----- ESTILOS -----
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
style.configure("Blue.Treeview", font=("Segoe UI", 10), rowheight=26, borderwidth=0)
style.map("Blue.Treeview", background=[("selected", "#cfe8ff")])
style.configure("Blue.Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=6)

# Layout principal
paned = ttk.PanedWindow(root, orient='horizontal'); paned.pack(fill='both', expand=True, padx=8, pady=8)

# ----- Izquierda: editor con gutter -----
left = ttk.Frame(paned); left.configure(padding=0)
ttk.Label(left, text="Entrada", style="Title.TLabel").pack(anchor='w')

editor_frame = ttk.Frame(left); editor_frame.pack(fill='both', expand=True, pady=(4,6))
ys = ttk.Scrollbar(editor_frame, orient='vertical'); ys.pack(side='right', fill='y')

gutter = LineNumbers(editor_frame, None, bg="#f3f4f6"); gutter.pack(side='left', fill='y')

editor = tk.Text(editor_frame, height=25, wrap='none', font=("Consolas", 11), undo=True)
editor.pack(side='left', fill='both', expand=True); gutter.textwidget = editor

def _sync_scroll(first, last):
    ys.set(first, last); gutter.redraw()
editor.configure(yscrollcommand=_sync_scroll)
ys.config(command=editor.yview)

xs = ttk.Scrollbar(left, orient='horizontal', command=editor.xview)
editor.configure(xscrollcommand=xs.set); xs.pack(fill='x')

def _on_any_change(event=None): gutter.redraw()
for seq in ("<KeyRelease>", "<MouseWheel>", "<Button-4>", "<Button-5>", "<Configure>", "<Visibility>"):
    editor.bind(seq, _on_any_change)

def _on_modified(event=None):
    editor.edit_modified(False); gutter.redraw()
editor.bind("<<Modified>>", _on_modified)

def _tick():
    gutter.redraw(); root.after(120, _tick)
root.after(200, _tick)

btns = ttk.Frame(left); btns.pack(anchor='e', pady=(2,0))
ttk.Button(btns, text="Analizar", command=analizar).pack(side='left', padx=(0,8))
ttk.Button(btns, text="Limpiar",  command=limpiar).pack(side='left')

paned.add(left, weight=1)

# ----- Derecha: pestañas -----
right = ttk.Frame(paned); paned.add(right, weight=1)
notebook = ttk.Notebook(right); notebook.pack(fill='both', expand=True)

def make_scrolled_tree(parent, columns, height=14, style_name="Blue.Treeview"):
    frame = ttk.Frame(parent)
    yscroll = ttk.Scrollbar(frame, orient='vertical')
    xscroll = ttk.Scrollbar(frame, orient='horizontal')
    tv = ttk.Treeview(
        frame, columns=columns, show="headings", height=height,
        style=style_name, yscrollcommand=yscroll.set, xscrollcommand=xscroll.set
    )
    yscroll.config(command=tv.yview); yscroll.pack(side='right', fill='y')
    xscroll.config(command=tv.xview); xscroll.pack(side='bottom', fill='x')
    tv.pack(side='left', fill='both', expand=True)
    return frame, tv

# Lexemas
tab_lex = ttk.Frame(notebook); notebook.add(tab_lex, text="Lexemes")
sym_frame, sym_table = make_scrolled_tree(tab_lex, ("Lexema","Tipo"), height=16)
sym_table.heading("Lexema", text="Lexema"); sym_table.heading("Tipo", text="Tipo")
sym_table.column("Lexema", width=360, anchor="w", stretch=True)
sym_table.column("Tipo",   width=140, anchor="center")
sym_frame.pack(fill='both', expand=True, padx=6, pady=6)

# Errores
tab_err = ttk.Frame(notebook); notebook.add(tab_err, text="Errors")
err_frame, err_table = make_scrolled_tree(tab_err, ("Token","Lexema","Renglón","Descripción"), height=16)
for col, w, anchor in (("Token",90,"center"), ("Lexema",260,"w"), ("Renglón",90,"center"), ("Descripción",520,"w")):
    err_table.heading(col, text=col); err_table.column(col, width=w, anchor=anchor, stretch=(col=="Descripción"))
err_frame.pack(fill='both', expand=True, padx=6, pady=6)

# Triplos
tab_tri = ttk.Frame(notebook); notebook.add(tab_tri, text="Triples")
tri_headers = ["#", "OP", "DO", "DF"]
tri_headers_ui = ("#", "OP", "DO", "DF", "Explicación")
tri_frame, tri_table = make_scrolled_tree(tab_tri, tri_headers_ui, height=18)
for col in tri_headers_ui: tri_table.heading(col, text=col)

col_widths  = {"#": 60, "OP": 120, "DO": 360, "DF": 520, "Explicación": 360}
col_mins    = {"#": 40, "OP": 80,  "DO": 160, "DF": 200, "Explicación": 160}
col_anchors = {"#": "center", "OP": "center", "DO": "w",  "DF": "w",  "Explicación": "w"}
for col in tri_headers_ui:
    tri_table.column(
        col,
        width=col_widths.get(col,120),
        minwidth=col_mins.get(col,60),
        anchor=col_anchors.get(col,"center"),
        stretch=True
    )
tri_frame.pack(fill='both', expand=True, padx=6, pady=6)

# Zebra rows + estilo para filas visuales
sym_table.tag_configure("odd",  background="#f7f7fb")
sym_table.tag_configure("even", background="#ffffff")
err_table.tag_configure("odd",  background="#f7f7fb")
err_table.tag_configure("even", background="#ffffff")
tri_table.tag_configure("odd",  background="#f7f7fb")
tri_table.tag_configure("even", background="#ffffff")
tri_table.tag_configure("ghost", foreground="#6b7280")  # gris tenue para BEGIN/END/JUMP/TRUE/FALSE/IF NOT

# Atajo y arranque
root.bind("<Control-l>", lambda e: limpiar())
root.after_idle(gutter.redraw)
root.mainloop()
