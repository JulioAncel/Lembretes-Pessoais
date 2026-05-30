"""Preview de 3 estilos visuais para o Notificador de Lembretes."""
import tkinter as tk
from tkinter import ttk

# ── dados de exemplo ──────────────────────────────────────────────────────────
SAMPLE = {"name": "Encomendas", "website": "https://meusite.com.br",
          "interval": "60", "start": "08:00", "end": "18:00"}

# ──────────────────────────────────────────────────────────────────────────────
# ESTILO 1 — Dark / Roxo (parecido com o popup atual)
# ──────────────────────────────────────────────────────────────────────────────
def estilo_dark(root):
    BG      = "#1e1e2e"
    BG2     = "#2a2a3e"
    ACCENT  = "#7c6af7"
    DANGER  = "#f87171"
    FG      = "#e2e8f0"
    ENTRY   = "#2d2d44"

    w = tk.Toplevel(root)
    w.title("Estilo 1 — Dark")
    w.configure(bg=BG)
    w.resizable(False, False)

    # Header
    hdr = tk.Frame(w, bg=BG2, pady=8)
    hdr.pack(fill="x")
    tk.Label(hdr, text="Lembretes", font=("Segoe UI", 12, "bold"),
             bg=BG2, fg=FG).pack(side="left", padx=14)

    body = tk.Frame(w, bg=BG, padx=14, pady=10)
    body.pack(fill="both")

    # Cabeçalhos das colunas
    for col, (txt, w_) in enumerate([("Nome",14),("Website",24),("Interv.",8),("Início",6),("Fim",6)]):
        tk.Label(body, text=txt, font=("Segoe UI", 8, "bold"),
                 bg=BG, fg="#94a3b8", width=w_, anchor="w").grid(row=0, column=col, padx=3, pady=(0,4), sticky="w")

    # Linha de exemplo
    vals = [SAMPLE["name"], SAMPLE["website"], SAMPLE["interval"], SAMPLE["start"], SAMPLE["end"]]
    widths = [14, 24, 8, 6, 6]
    for col, (val, wd) in enumerate(zip(vals, widths)):
        e = tk.Entry(body, width=wd, bg=ENTRY, fg=FG, insertbackground=FG,
                     relief="flat", highlightthickness=1,
                     highlightbackground="#3d3d5c", highlightcolor=ACCENT)
        e.insert(0, val)
        e.grid(row=1, column=col, padx=3, pady=3, ipady=4)

    tk.Button(body, text="Salvar", bg=ACCENT, fg="white", relief="flat",
              font=("Segoe UI", 9), padx=10, cursor="hand2",
              activebackground="#6a5ae0", activeforeground="white"
              ).grid(row=1, column=5, padx=(8,3), pady=3)
    tk.Button(body, text="Excluir", bg=DANGER, fg="white", relief="flat",
              font=("Segoe UI", 9), padx=8, cursor="hand2",
              activebackground="#ef4444", activeforeground="white"
              ).grid(row=1, column=6, padx=3, pady=3)

    # Rodapé
    foot = tk.Frame(w, bg=BG, pady=8)
    foot.pack(fill="x", padx=14)
    tk.Button(foot, text="＋  Adicionar lembrete", bg=BG2, fg=FG,
              relief="flat", font=("Segoe UI", 9), padx=12, cursor="hand2",
              activebackground="#3a3a5c", activeforeground=FG
              ).pack(side="left")

    w.geometry("+80+200")


# ──────────────────────────────────────────────────────────────────────────────
# ESTILO 2 — Claro / Clean
# ──────────────────────────────────────────────────────────────────────────────
def estilo_claro(root):
    BG      = "#ffffff"
    BG2     = "#f1f5f9"
    ACCENT  = "#2563eb"
    DANGER  = "#dc2626"
    FG      = "#1e293b"
    BORDER  = "#cbd5e1"

    w = tk.Toplevel(root)
    w.title("Estilo 2 — Claro")
    w.configure(bg=BG)
    w.resizable(False, False)

    hdr = tk.Frame(w, bg=BG2, pady=9)
    hdr.pack(fill="x")
    # Barra colorida no topo
    tk.Frame(w, bg=ACCENT, height=3).place(x=0, y=0, relwidth=1)
    tk.Label(hdr, text="Lembretes", font=("Segoe UI", 12, "bold"),
             bg=BG2, fg=FG).pack(side="left", padx=14)

    body = tk.Frame(w, bg=BG, padx=14, pady=10)
    body.pack(fill="both")

    for col, (txt, w_) in enumerate([("Nome",14),("Website",24),("Interv.",8),("Início",6),("Fim",6)]):
        tk.Label(body, text=txt, font=("Segoe UI", 8, "bold"),
                 bg=BG, fg="#64748b", width=w_, anchor="w").grid(row=0, column=col, padx=3, pady=(0,4), sticky="w")

    vals   = [SAMPLE["name"], SAMPLE["website"], SAMPLE["interval"], SAMPLE["start"], SAMPLE["end"]]
    widths = [14, 24, 8, 6, 6]
    for col, (val, wd) in enumerate(zip(vals, widths)):
        e = tk.Entry(body, width=wd, bg=BG, fg=FG, relief="flat",
                     highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
        e.insert(0, val)
        e.grid(row=1, column=col, padx=3, pady=3, ipady=4)

    tk.Button(body, text="Salvar", bg=ACCENT, fg="white", relief="flat",
              font=("Segoe UI", 9), padx=10, cursor="hand2",
              activebackground="#1d4ed8", activeforeground="white"
              ).grid(row=1, column=5, padx=(8,3), pady=3)
    tk.Button(body, text="Excluir", bg="#fee2e2", fg=DANGER, relief="flat",
              font=("Segoe UI", 9), padx=8, cursor="hand2",
              activebackground="#fecaca", activeforeground=DANGER
              ).grid(row=1, column=6, padx=3, pady=3)

    foot = tk.Frame(w, bg=BG2, pady=8)
    foot.pack(fill="x", padx=0)
    tk.Button(foot, text="＋  Adicionar lembrete", bg=BG2, fg=ACCENT,
              relief="flat", font=("Segoe UI", 9, "bold"), padx=12, cursor="hand2",
              activebackground="#e2e8f0", activeforeground=ACCENT
              ).pack(side="left", padx=14)

    w.geometry("+560+200")


# ──────────────────────────────────────────────────────────────────────────────
# ESTILO 3 — Verde / Profissional
# ──────────────────────────────────────────────────────────────────────────────
def estilo_verde(root):
    BG      = "#f8fafc"
    HDR_BG  = "#0f4c35"
    HDR_FG  = "#ffffff"
    ACCENT  = "#16a34a"
    DANGER  = "#dc2626"
    FG      = "#1e293b"
    ENTRY   = "#ffffff"
    BORDER  = "#bbf7d0"

    w = tk.Toplevel(root)
    w.title("Estilo 3 — Verde")
    w.configure(bg=BG)
    w.resizable(False, False)

    hdr = tk.Frame(w, bg=HDR_BG, pady=10)
    hdr.pack(fill="x")
    tk.Label(hdr, text="Lembretes", font=("Segoe UI", 12, "bold"),
             bg=HDR_BG, fg=HDR_FG).pack(side="left", padx=14)

    body = tk.Frame(w, bg=BG, padx=14, pady=10)
    body.pack(fill="both")

    for col, (txt, w_) in enumerate([("Nome",14),("Website",24),("Interv.",8),("Início",6),("Fim",6)]):
        tk.Label(body, text=txt, font=("Segoe UI", 8, "bold"),
                 bg=BG, fg="#475569", width=w_, anchor="w").grid(row=0, column=col, padx=3, pady=(0,4), sticky="w")

    vals   = [SAMPLE["name"], SAMPLE["website"], SAMPLE["interval"], SAMPLE["start"], SAMPLE["end"]]
    widths = [14, 24, 8, 6, 6]
    for col, (val, wd) in enumerate(zip(vals, widths)):
        e = tk.Entry(body, width=wd, bg=ENTRY, fg=FG, relief="flat",
                     highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
        e.insert(0, val)
        e.grid(row=1, column=col, padx=3, pady=3, ipady=4)

    tk.Button(body, text="Salvar", bg=ACCENT, fg="white", relief="flat",
              font=("Segoe UI", 9), padx=10, cursor="hand2",
              activebackground="#15803d", activeforeground="white"
              ).grid(row=1, column=5, padx=(8,3), pady=3)
    tk.Button(body, text="Excluir", bg="#fee2e2", fg=DANGER, relief="flat",
              font=("Segoe UI", 9), padx=8, cursor="hand2",
              activebackground="#fecaca", activeforeground=DANGER
              ).grid(row=1, column=6, padx=3, pady=3)

    foot = tk.Frame(w, bg=BG, pady=8)
    foot.pack(fill="x", padx=14)
    tk.Button(foot, text="＋  Adicionar lembrete", bg=HDR_BG, fg=HDR_FG,
              relief="flat", font=("Segoe UI", 9), padx=12, cursor="hand2",
              activebackground="#1a6348", activeforeground=HDR_FG
              ).pack(side="left")

    w.geometry("+1040+200")


# ── main ──────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.withdraw()

estilo_dark(root)
estilo_claro(root)
estilo_verde(root)

root.mainloop()
