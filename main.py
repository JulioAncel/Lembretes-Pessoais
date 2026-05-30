import tkinter as tk
from tkinter import ttk, messagebox
import json, os, uuid, threading, time, sys, gc, queue
import math, struct, io, wave, winsound
from datetime import datetime, timedelta, time as dtime

if getattr(sys, "frozen", False):
    BASE_DIR   = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

CONFIG_FILE = os.path.join(BASE_DIR,   "reminders.json")
ICON_FILE   = os.path.join(BUNDLE_DIR, "icon.ico")

# ---------------------------------------------------------------------------
# Chime
# ---------------------------------------------------------------------------

def _build_chime() -> bytes:
    rate   = 44100
    # Dó5 → Mi5 → Sol5 — suave e curto
    notes  = [(523, 0.13), (659, 0.13), (784, 0.28)]
    frames = []
    for freq, dur in notes:
        n       = int(rate * dur)
        fade_in = int(n * 0.06)
        fade_out= int(n * 0.45)
        for i in range(n):
            if   i < fade_in:              env = i / fade_in
            elif i > n - fade_out:         env = (n - i) / fade_out
            else:                          env = 1.0
            v = int(env * 0.22 * 32767 * math.sin(2 * math.pi * freq * i / rate))
            frames.append(v)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack(f"<{len(frames)}h", *frames))
    return buf.getvalue()

_CHIME = _build_chime()

def play_chime():
    threading.Thread(
        target=lambda: winsound.PlaySound(_CHIME, winsound.SND_MEMORY),
        daemon=True
    ).start()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_config_mtime = 0.0
_config_cache = []

def load_reminders():
    global _config_mtime, _config_cache
    if not os.path.exists(CONFIG_FILE):
        return []
    mtime = os.path.getmtime(CONFIG_FILE)
    if mtime != _config_mtime:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
        _config_mtime = mtime
    return _config_cache

def save_reminders(reminders):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

_last_notified = {}
_lock          = threading.Lock()
_root_ref      = None
_notif_queue   = queue.Queue()

POPUP_DURATION_MS = 60_000   # 1 minuto

def fire_notification(reminder):
    _notif_queue.put(reminder)

def _poll_notifications():
    try:
        while True:
            reminder = _notif_queue.get_nowait()
            _show_popup(reminder)
    except queue.Empty:
        pass
    if _root_ref:
        _root_ref.after(500, _poll_notifications)

def _show_popup(reminder):
    import webbrowser
    play_chime()

    website = reminder.get("website", "").strip()

    popup = tk.Toplevel(_root_ref)
    popup.title("Lembrete")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.configure(bg="#1e1e2e")

    if os.path.exists(ICON_FILE):
        try:
            popup.iconbitmap(ICON_FILE)
        except Exception:
            pass

    # Posição: canto inferior direito
    w, h = 300, 100
    sw = _root_ref.winfo_screenwidth()
    sh = _root_ref.winfo_screenheight()
    popup.geometry(f"{w}x{h}+{sw - w - 16}+{sh - h - 60}")
    popup.update_idletasks()
    popup.attributes("-topmost", True)
    popup.lift()

    tk.Label(popup, text=reminder["name"],
             font=("Segoe UI", 12, "bold"),
             bg="#1e1e2e", fg="#ffffff",
             anchor="center").pack(fill="x", padx=12, pady=(12, 6))

    btn_frame = tk.Frame(popup, bg="#1e1e2e")
    btn_frame.pack()

    def do_close():
        try:
            popup.destroy()
        except Exception:
            pass

    def do_web():
        if website:
            webbrowser.open(website)
        do_close()

    tk.Button(btn_frame, text="Fechar", command=do_close,
              font=("Segoe UI", 9), bg="#3a3a5c", fg="#ffffff",
              relief="flat", padx=10, cursor="hand2"
              ).pack(side="left", padx=6)

    if website:
        tk.Button(btn_frame, text="Abrir web", command=do_web,
                  font=("Segoe UI", 9), bg="#5865f2", fg="#ffffff",
                  relief="flat", padx=10, cursor="hand2"
                  ).pack(side="left", padx=6)

    popup.after(POPUP_DURATION_MS, do_close)

# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

def scheduler_loop():
    while True:
        now = datetime.now()
        cur = now.time().replace(second=0, microsecond=0)

        for reminder in load_reminders():
            rid = reminder["id"]
            try:
                sh, sm = map(int, reminder["start_time"].split(":"))
                eh, em = map(int, reminder["end_time"].split(":"))
            except Exception:
                continue

            if not (dtime(sh, sm) <= cur <= dtime(eh, em)):
                continue

            interval = timedelta(minutes=reminder["interval_minutes"])
            with _lock:
                last = _last_notified.get(rid)

            if last is None or (now - last) >= interval:
                with _lock:
                    _last_notified[rid] = now
                fire_notification(reminder)

        time.sleep(30)

# ---------------------------------------------------------------------------
# Tray
# ---------------------------------------------------------------------------

def start_tray(root):
    import pystray
    from PIL import Image

    if os.path.exists(ICON_FILE):
        img = Image.open(ICON_FILE).resize((64, 64)).convert("RGBA")
    else:
        from PIL import ImageDraw
        img = Image.new("RGBA", (64, 64), (35, 95, 195, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([28, 14, 36, 40], fill=(255, 255, 255))
        d.ellipse([26, 42, 38, 52], fill=(255, 255, 255))

    def on_open(icon=None, item=None):
        root.after(0, root.deiconify)

    def on_quit(icon, item):
        icon.stop()
        root.after(0, root.destroy)

    icon = pystray.Icon(
        "notificador", img, "Notificador de Lembretes",
        menu=pystray.Menu(
            pystray.MenuItem("Abrir", on_open, default=True),
            pystray.MenuItem("Sair", on_quit),
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()

# ---------------------------------------------------------------------------
# Tema
# ---------------------------------------------------------------------------

T = {
    "bg":      "#1e1e2e",
    "bg2":     "#2a2a3e",
    "entry":   "#2d2d44",
    "border":  "#3d3d5c",
    "accent":  "#7c6af7",
    "danger":  "#f87171",
    "fg":      "#e2e8f0",
    "fg_dim":  "#94a3b8",
}

# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

_COLS = [
    ("Nome",            13),
    ("Website",         28),
    ("Intervalo (min)", 11),
    ("Início",           6),
    ("Fim",              6),
]

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notificador de Lembretes")
        self.root.resizable(False, False)
        self.root.configure(bg=T["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self.root.withdraw)
        self.root.bind("<Map>", lambda e: self.root.lift())

        if os.path.exists(ICON_FILE):
            try:
                self.root.iconbitmap(ICON_FILE)
            except Exception:
                pass

        self.rows = []
        self._next_row = 1
        self._build_ui()
        self._load_into_ui()

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=T["bg2"], pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Lembretes", font=("Segoe UI", 12, "bold"),
                 bg=T["bg2"], fg=T["fg"]).pack(side="left", padx=14)

        self.inner = tk.Frame(self.root, bg=T["bg"])
        self.inner.pack(fill="both", expand=True, padx=10, pady=5)

        for col, (text, w) in enumerate(_COLS):
            tk.Label(self.inner, text=text, font=("Segoe UI", 8, "bold"),
                     bg=T["bg"], fg=T["fg_dim"], width=w, anchor="w"
                     ).grid(row=0, column=col, padx=3, pady=(6, 3), sticky="w")
        for col in (5, 6):
            tk.Label(self.inner, text="", bg=T["bg"]).grid(row=0, column=col)

        bottom = tk.Frame(self.root, bg=T["bg"], pady=8)
        bottom.pack(fill="x", padx=12)
        tk.Button(bottom, text="＋  Adicionar lembrete",
                  command=self._add_row,
                  font=("Segoe UI", 9), bg=T["bg2"], fg=T["fg"],
                  relief="flat", padx=12, cursor="hand2",
                  activebackground="#3a3a5c", activeforeground=T["fg"]
                  ).pack(side="left")

    def _add_row(self, reminder=None):
        rid = reminder["id"] if reminder else str(uuid.uuid4())
        r = self._next_row
        self._next_row += 1

        widths  = [w for _, w in _COLS]
        entries = [
            tk.Entry(self.inner, width=w,
                     bg=T["entry"], fg=T["fg"],
                     insertbackground=T["fg"],
                     relief="flat",
                     highlightthickness=1,
                     highlightbackground=T["border"],
                     highlightcolor=T["accent"])
            for w in widths
        ]
        e_name, e_website, e_interval, e_start, e_end = entries

        if reminder:
            e_name.insert(0,     reminder.get("name", ""))
            e_website.insert(0,  reminder.get("website", ""))
            e_interval.insert(0, str(reminder.get("interval_minutes", 60)))
            e_start.insert(0,    reminder.get("start_time", "08:00"))
            e_end.insert(0,      reminder.get("end_time", "18:00"))
        else:
            e_interval.insert(0, "60")
            e_start.insert(0,    "08:00")
            e_end.insert(0,      "18:00")

        for col, entry in enumerate(entries):
            entry.grid(row=r, column=col, padx=3, pady=3, ipady=3, sticky="w")

        btn_save = tk.Button(
            self.inner, text="Salvar", font=("Segoe UI", 8),
            bg=T["accent"], fg="white", relief="flat", padx=8, cursor="hand2",
            activebackground="#6a5ae0", activeforeground="white",
            command=lambda: self._save_row(rid, e_name, e_website, e_interval, e_start, e_end)
        )
        btn_del = tk.Button(
            self.inner, text="Excluir", font=("Segoe UI", 8),
            bg=T["bg2"], fg=T["danger"], relief="flat", padx=8, cursor="hand2",
            activebackground="#3a3a5c", activeforeground=T["danger"],
            command=lambda: self._delete_row(rid)
        )
        btn_save.grid(row=r, column=5, padx=(8, 3), pady=3)
        btn_del.grid(row=r, column=6, padx=3, pady=3)

        self.rows.append({
            "id": rid,
            "widgets": entries + [btn_save, btn_del]
        })

    def _save_row(self, rid, e_name, e_website, e_interval, e_start, e_end):
        name    = e_name.get().strip()
        website = e_website.get().strip()
        intv    = e_interval.get().strip()
        start   = e_start.get().strip()
        end     = e_end.get().strip()

        if not name:
            messagebox.showwarning("Aviso", "Preencha o nome do lembrete.")
            return
        try:
            intv_int = int(intv)
            if intv_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Intervalo deve ser um número inteiro positivo (em minutos).")
            return
        for val, label in [(start, "Início"), (end, "Fim")]:
            try:
                h, m = val.split(":")
                assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
            except Exception:
                messagebox.showwarning("Aviso", f"Horário '{label}' inválido. Use o formato HH:MM.")
                return

        reminders = load_reminders()
        data = {"id": rid, "name": name, "website": website,
                "interval_minutes": intv_int, "start_time": start, "end_time": end}
        idx = next((i for i, rv in enumerate(reminders) if rv["id"] == rid), None)
        if idx is not None:
            reminders[idx] = data
        else:
            reminders.append(data)
        save_reminders(reminders)
        messagebox.showinfo("✓  Salvo", f"Lembrete '{name}' salvo.")

    def _delete_row(self, rid):
        if not messagebox.askyesno("Confirmar", "Excluir este lembrete?"):
            return
        row_data = next((r for r in self.rows if r["id"] == rid), None)
        if row_data:
            for w in row_data["widgets"]:
                w.destroy()
            self.rows = [r for r in self.rows if r["id"] != rid]
        save_reminders([r for r in load_reminders() if r["id"] != rid])

    def _load_into_ui(self):
        for r in load_reminders():
            self._add_row(r)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    threading.Thread(target=scheduler_loop, daemon=True).start()

    root = tk.Tk()
    _root_ref = root
    ReminderApp(root)
    start_tray(root)
    root.after(500, _poll_notifications)

    gc.collect()
    root.mainloop()
