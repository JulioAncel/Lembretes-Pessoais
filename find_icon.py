"""Diagnóstico: encontra de onde vem o ícone da peninha no tkinter."""
import tkinter as tk
import ctypes, ctypes.wintypes as wt

root = tk.Tk()
root.update()
hwnd = root.winfo_id()

# Nome da classe da janela
cn = ctypes.create_unicode_buffer(256)
ctypes.windll.user32.GetClassNameW(hwnd, cn, 256)
print(f"Classe da janela: {cn.value}")

# Tentativas de obter o HICON
for label, handle in [
    ("GetClassLongPtr GCL_HICON (-14)",    ctypes.windll.user32.GetClassLongPtrW(hwnd, -14)),
    ("GetClassLongPtr GCLP_HICONSM (-34)", ctypes.windll.user32.GetClassLongPtrW(hwnd, -34)),
    ("WM_GETICON ICON_BIG (1)",            ctypes.windll.user32.SendMessageW(hwnd, 0x007F, 1, 0)),
    ("WM_GETICON ICON_SMALL (0)",          ctypes.windll.user32.SendMessageW(hwnd, 0x007F, 0, 0)),
    ("WM_GETICON ICON_SMALL2 (2)",         ctypes.windll.user32.SendMessageW(hwnd, 0x007F, 2, 0)),
]:
    print(f"  {label}: {handle}")

# Janela pai
parent = ctypes.windll.user32.GetParent(hwnd)
print(f"\nParent HWND: {parent}")
if parent:
    for label, handle in [
        ("Parent GCL_HICON",   ctypes.windll.user32.GetClassLongPtrW(parent, -14)),
        ("Parent WM_GETICON",  ctypes.windll.user32.SendMessageW(parent, 0x007F, 1, 0)),
    ]:
        print(f"  {label}: {handle}")

root.destroy()

# Tenta extrair de DLLs do Tk
import os, sys
py_dir = os.path.dirname(sys.executable)
candidates = [
    os.path.join(py_dir, "DLLs", "tk86t.dll"),
    os.path.join(py_dir, "DLLs", "_tkinter.pyd"),
    os.path.join(py_dir, "tcl", "tk8.6", "wish86t.exe"),
]
large = (ctypes.c_size_t * 1)()
small = (ctypes.c_size_t * 1)()
print()
for f in candidates:
    if os.path.exists(f):
        n = ctypes.windll.shell32.ExtractIconExW(f, 0, large, small, 1)
        print(f"{os.path.basename(f)}: {n} ícone(s), handle={large[0]}")
        if large[0]:
            ctypes.windll.user32.DestroyIcon(large[0])
    else:
        print(f"{os.path.basename(f)}: não encontrado")
