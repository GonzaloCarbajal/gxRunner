import os
import sys
import ctypes
import subprocess
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except:
        pass
    sys.exit()

def discover_genexus_versions():
    base_paths = [r"C:\Program Files (x86)\GeneXus", r"C:\Program Files\GeneXus", r"C:\GeneXus"]
    discovered = []
    for base in base_paths:
        if not os.path.exists(base): continue
        try:
            for folder in os.listdir(base):
                path = os.path.join(base, folder, "GeneXus.exe")
                if os.path.exists(path):
                    discovered.append({"Nombre": folder, "Ruta": path})
        except: continue
    discovered.sort(key=lambda x: x["Nombre"].lower())
    return discovered

def discover_kbs():
    kb_paths = [r"C:\KBs", r"C:\Models"]
    discovered = []
    for base in kb_paths:
        if not os.path.exists(base): continue
        try:
            for folder in os.listdir(base):
                full_path = os.path.join(base, folder)
                if os.path.isdir(full_path):
                    try:
                        if any(f.lower().endswith(".gxw") for f in os.listdir(full_path)):
                            discovered.append((folder, full_path))
                    except: continue
        except: continue
    discovered.sort(key=lambda x: x[0].lower())
    return discovered

def ensure_default_config(config_path="conf.json"):
    if os.path.exists(config_path): return
    try:
        vers = discover_genexus_versions()
        if not vers:
            vers = [{"Nombre": "GeneXus 18", "Ruta": r"C:\Program Files (x86)\GeneXus\GeneXus18\GeneXus.exe"}]
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(vers, f, indent=4)
    except: pass

def load_versions(config_path="conf.json"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return [(i["Nombre"], i["Ruta"]) for i in json.load(f)]
    except: return []

def open_config_file(event=None):
    config_path = os.path.abspath("conf.json")
    try:
        use_picker = False
        if event and hasattr(event, 'state'):
            use_picker = bool(event.state & 0x0004) or bool(event.state & 0x0001)
        
        if use_picker:
            app = filedialog.askopenfilename(title="Elegir editor", filetypes=[("EXE", "*.exe")])
            if app: subprocess.Popen([app, config_path])
        else:
            os.startfile(config_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_action(install_first=False):
    # Obtener valores actuales de la UI
    name = combo_ver.get()
    exe = ""
    for n, p in VERSIONS:
        if n == name: 
            exe = p
            break
    
    if not exe or not os.path.exists(exe):
        messagebox.showerror("Error", "No se encuentra GeneXus.exe")
        return

    kb_name = combo_kb.get()
    kb_path = ""
    if kb_name != "Ninguna":
        for n, p in KBS:
            if n == kb_name:
                kb_path = p
                break

    def launch_gx():
        """Función interna para lanzar GeneXus"""
        cmd = [exe]
        if kb_path:
            cmd.append(f"/KB:{kb_path}")
        subprocess.Popen(cmd, cwd=os.path.dirname(exe))

    if not install_first:
        # Si es solo abrir, lo hacemos directo sin barra
        launch_gx()
        status.set("GeneXus abierto")
        return

    # Si es con INSTALL, activamos la barra y bloqueamos UI
    btn_run.config(state="disabled")
    btn_install.config(state="disabled")
    progress.pack(pady=10, padx=20, fill="x") # Mostrar barra
    progress["mode"] = "indeterminate"
    progress.start(10)
    status.set("Procesando /install...")

    def task():
        try:
            working_dir = os.path.dirname(exe)
            # Ejecutar Install
            subprocess.run([exe, "/install"], capture_output=True, cwd=working_dir)
            # Lanzar GeneXus
            launch_gx()
            status.set("Listo")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la ejecución:\n{e}")
            status.set("Error")
        finally:
            root.after(0, reset_ui)

    def reset_ui():
        progress.stop()
        progress.pack_forget() # Ocultar barra al terminar
        btn_run.config(state="normal")
        btn_install.config(state="normal")

    threading.Thread(target=task, daemon=True).start()

# --- Configuración UI ---
ensure_default_config()
VERSIONS = load_versions()
KBS = discover_kbs()

root = tk.Tk()
root.title("GeneXus Launcher")
root.geometry("500x380")

status = tk.StringVar(value="Listo")

ttk.Label(root, text="Versión de GeneXus:").pack(pady=(15,5))
combo_ver = ttk.Combobox(root, values=[v[0] for v in VERSIONS], state="readonly")
if VERSIONS: combo_ver.current(0)
combo_ver.pack(padx=20, fill="x")

ttk.Label(root, text="Knowledge Base:").pack(pady=(10,5))
combo_kb = ttk.Combobox(root, values=["Ninguna"] + [k[0] for k in KBS], state="readonly")
combo_kb.current(0)
combo_kb.pack(padx=20, fill="x")

btn_run = ttk.Button(root, text="Abrir GeneXus", command=lambda: run_action(False))
btn_run.pack(pady=(20,5))

btn_install = ttk.Button(root, text="(/install) + Abrir", command=lambda: run_action(True))
btn_install.pack(pady=5)

btn_conf = ttk.Button(root, text="Abrir conf.json", command=open_config_file)
btn_conf.pack(pady=5)
btn_conf.bind("<Button-1>", open_config_file)

# La barra ahora se crea pero NO se empaqueta inicialmente
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
# progress.pack(...)  <-- Quitamos el pack de aquí

ttk.Label(root, textvariable=status, foreground="blue").pack(pady=5)

root.mainloop()
