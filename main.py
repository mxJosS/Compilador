import tkinter as tk
from tkinter import ttk
from parser import parser, symbol_table, error_table
from lexer import lexer as lex_inst
def analizar():
    # Limpiar tablas
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    symbol_table.clear()
    error_table.clear()

    codigo = editor.get("1.0", tk.END)

 
    lex_inst.lineno = 1
    parser.parse(codigo, lexer=lex_inst)


    # Poblar tabla de símbolos (sin duplicados)
    for lexema, tipo in symbol_table.rows():
        sym_table.insert('', 'end', values=(lexema, tipo))

    # Poblar tabla de errores
    for token, lexema, renglon, desc in error_table.rows():
        err_table.insert('', 'end', values=(token, lexema, renglon, desc))

def limpiar():
    editor.delete("1.0", tk.END)                 # borra el texto
    for w in sym_table.get_children(): sym_table.delete(w)
    for w in err_table.get_children(): err_table.delete(w)
    symbol_table.clear()
    error_table.clear()
    lex_inst.lineno = 1  
    
root = tk.Tk()
root.title("Compilador U1 - Automatas II (FOR)")
root.geometry("1050x640")

# Estilos
style = ttk.Style(root)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Blue.Treeview", font=("Segoe UI", 10), rowheight=24)
style.map("Treeview", background=[('selected', '#cfe8ff')])

# Layout principal
paned = ttk.PanedWindow(root, orient='horizontal')
paned.pack(fill='both', expand=True, padx=8, pady=8)

# ---- Izquierda: Editor de entrada ----
left = ttk.Frame(paned)
lbl_in = ttk.Label(left, text="Entrada", font=("Segoe UI", 11, "bold"))
lbl_in.pack(anchor='w')

editor = tk.Text(left, height=25, wrap='none', font=("Consolas", 11))
editor.pack(fill='both', expand=True, pady=(4,6))

# Botones Analizar y Limpiar
btns = ttk.Frame(left)
btns.pack(anchor='e', pady=(2,0))

btn_analizar = ttk.Button(btns, text="Analizar", command=analizar)
btn_analizar.pack(side='left', padx=(0,8))

btn_limpiar = ttk.Button(btns, text="Limpiar", command=limpiar)
btn_limpiar.pack(side='left')

# >>> ESTE ERA EL QUE FALTABA <<<
paned.add(left, weight=1)

# ---- Derecha: Tablas ----
right = ttk.Frame(paned)
paned.add(right, weight=1)

# Tabla de símbolos
ttk.Label(right, text="Tabla de símbolos", font=("Segoe UI", 11, "bold")).pack(anchor='w')
sym_table = ttk.Treeview(
    right, columns=("Lexema","Tipo"), show="headings", height=12, style="Blue.Treeview"
)
sym_table.heading("Lexema", text="Lexema")
sym_table.heading("Tipo", text="Tipo")
sym_table.column("Lexema", width=220, anchor='w')
sym_table.column("Tipo",   width=120, anchor='w')
sym_table.pack(fill='x', pady=(4,10))

# Tabla de errores
ttk.Label(right, text="Tabla de errores", font=("Segoe UI", 11, "bold")).pack(anchor='w')
err_table = ttk.Treeview(
    right, columns=("Token","Lexema","Renglón","Descripción"),
    show="headings", height=12, style="Blue.Treeview"
)
for col, w in (("Token",100), ("Lexema",160), ("Renglón",90), ("Descripción",380)):
    err_table.heading(col, text=col)
    err_table.column(col, width=w, anchor='w')
err_table.pack(fill='both', expand=True, pady=(4,0))

# Atajo para limpiar
root.bind("<Control-l>", lambda e: limpiar())

root.mainloop()
# Fin de main.py