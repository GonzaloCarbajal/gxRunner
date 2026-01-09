import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

VERSIONS = [
    ("GeneXus 18 U10", r"C:\Program Files (x86)\GeneXus\GeneXus18_U10\GeneXus.exe"),
    ("GeneXus 18",     r"C:\Program Files (x86)\GeneXus\GeneXus18\GeneXus.exe"),
    ("GeneXus 17",     r"C:\Program Files (x86)\GeneXus\GeneXus17\GeneXus.exe"),
]

def selected_exe() -> str:
    name = combo.get()
    for n, p in VERSIONS:
        if n == name:
            return p
    return ""

def run_install_and_open():
    exe = selected_exe()
    if not exe or not os.path.exists(exe):
        messagebox.showerror("Error", f"No existe GeneXus.exe en:\n{exe}")
        return

    # Obtenemos la carpeta donde está el .exe
    working_dir = os.path.dirname(exe)

    try:
        status.set("Ejecutando /install...")
        root.update_idletasks()

        # Agregamos cwd para mejorar compatibilidad y velocidad de carga
        res = subprocess.run([exe, "/install"], capture_output=True, text=True, cwd=working_dir)
        if res.returncode != 0:
            details = (res.stderr or res.stdout or "").strip()
            msg = "Falló /install.\n\n" \
                  f"ReturnCode: {res.returncode}\n"
            if details:
                msg += f"\nDetalle:\n{details}\n"
            msg += "\nSugerencia: ejecutá este launcher como Administrador."
            messagebox.showerror("GeneXus /install", msg)
            status.set("Error en /install")
            return

        status.set("Abriendo GeneXus...")
        root.update_idletasks()

        # Abrir normal con cwd
        subprocess.Popen([exe], cwd=working_dir)
        status.set("Listo")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ejecutar.\n\n{e}")
        status.set("Error")

def run_only_open():
    exe = selected_exe()
    if not exe or not os.path.exists(exe):
        messagebox.showerror("Error", f"No existe GeneXus.exe en:\n{exe}")
        return
    
    working_dir = os.path.dirname(exe)
    try:
        status.set("Abriendo GeneXus...")
        subprocess.Popen([exe], cwd=working_dir)
        status.set("Listo")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir.\n\n{e}")

root = tk.Tk()
root.title("GeneXus Launcher")
root.geometry("520x190")

ttk.Label(root, text="Versión:").pack(pady=(15, 5))

combo = ttk.Combobox(root, values=[v[0] for v in VERSIONS], state="readonly")
combo.current(0)
combo.pack(padx=15, fill="x")

# Botón principal rápido
ttk.Button(root, text="Abrir GeneXus", command=run_only_open).pack(pady=(15, 5))

# Botón para cuando sea necesario el install
ttk.Button(root, text="Reparar (/install) + Abrir", command=run_install_and_open).pack(pady=5)

status = tk.StringVar(value="Listo")
ttk.Label(root, textvariable=status).pack(pady=(0, 10))

ttk.Label(
    root,
    text="Nota: si /install falla, ejecutar como Administrador.",
).pack()

root.mainloop()
