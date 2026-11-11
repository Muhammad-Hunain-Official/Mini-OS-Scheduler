"""
Mini OS Scheduling Simulator  -  v3 "Aurora" UI (tkinter, no extra packages)

Matches the updated C program:
  * Algorithms : FCFS, SJF, Priority (non-preemptive), Round Robin (preemptive)
  * Process manager : add / update / delete / search (binary search by PID),
                      custom PIDs, max 10 processes
  * Save / Load  : processes.txt (same file format as the C program)
  * Compare      : average waiting time of all four algorithms
Extras : 3 live themes (Aurora / Sunset / Daylight), animated Gantt chart,
         Step mode, hover tooltips on the Gantt chart, toast notifications.

Run      : python gui.py
Shortcut : F5 = Run
"""
import math
import os
import random
import time
import tkinter as tk
from collections import deque
from tkinter import ttk
from types import SimpleNamespace

MAX = 10                      # same as #define MAX in the C code
LIMIT = 100000                # same upper bound the C code accepts
MAX_SLICES = 600              # keeps Round Robin drawable
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processes.txt")

# ------------------------------------------------------------- themes
THEMES = {
    "Aurora": dict(
        bg="#070b14", card="#0e1525", card2="#16203a", border="#233255",
        grid="#18233f", fg="#e9f0ff", muted="#8093ba", dim="#4b5a80",
        accent="#14b8a6", accent2="#8b5cf6", good="#4ade80", warn="#fbbf24",
        bad="#f87171", pink="#f472b6", neutral="#475569",
        hdr1="#0f766e", hdr2="#5b21b6", hsub="#c7f9f1",
        idle="#101831", idle_line="#3b4a78"),
    "Sunset": dict(
        bg="#150d14", card="#201320", card2="#2d1b2d", border="#4d2c49",
        grid="#2a1829", fg="#fff0ea", muted="#c79aa6", dim="#7d5568",
        accent="#ff7a59", accent2="#f59e0b", good="#86efac", warn="#fcd34d",
        bad="#fb7185", pink="#f472b6", neutral="#6b4a5e",
        hdr1="#be123c", hdr2="#f97316", hsub="#ffe4d6",
        idle="#261629", idle_line="#6b4568"),
    "Daylight": dict(
        bg="#edf1fa", card="#ffffff", card2="#f1f4fc", border="#d3dbef",
        grid="#e3e9f6", fg="#161d3a", muted="#66739a", dim="#a3aed0",
        accent="#4f46e5", accent2="#0891b2", good="#16a34a", warn="#d97706",
        bad="#e11d48", pink="#db2777", neutral="#64748b",
        hdr1="#4f46e5", hdr2="#06b6d4", hsub="#e0f2fe",
        idle="#eef2fb", idle_line="#aab6dc"),
}
T = SimpleNamespace()


def set_theme(name):
    T.__dict__.update(THEMES[name])
    T.name = name


COLORS = ["#ff6b81", "#ffa94d", "#ffd43b", "#69db7c", "#38d9a9",
          "#4dabf7", "#748ffc", "#b197fc", "#f783ac", "#a9e34b"]
ALGO_NAMES = {"FCFS": "FCFS", "SJF": "SJF",
              "PRIORITY": "Priority", "RR": "Round Robin"}
INK = "#0a0e1f"


# ------------------------------------------------------------- helpers
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    a, b = hex2rgb(c1), hex2rgb(c2)
    t = max(0.0, min(1.0, t))
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return blend(c, "#ffffff", t)


def darken(c, t):
    return blend(c, "#000000", t)


def ink(c):
    """Readable text colour (dark or white) for a given background."""
    r, g, b = hex2rgb(c)
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def rrect(c, x0, y0, x1, y1, r=10, **kw):
    r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return c.create_polygon(pts, smooth=True, **kw)


def binary_search(arr, left, right, pid, steps=1):
    """Recursive binary search by PID (same idea as the C code)."""
    if left > right:
        return -1, steps
    mid = (left + right) // 2
    if arr[mid]["pid"] == pid:
        return mid, steps
    if pid < arr[mid]["pid"]:
        return binary_search(arr, left, mid - 1, pid, steps + 1)
    return binary_search(arr, mid + 1, right, pid, steps + 1)


# ----------------------------------------------------------- scheduling
def schedule(procs, algo, quantum=2):
    """Returns (segments, info). segments: (pid|None, start, end).
    Same rules as the C program (array order breaks every tie):
      FCFS     -> sorted by arrival (stable)
      SJF      -> shortest burst, tie: earlier arrival
      PRIORITY -> smaller number = higher priority, tie: earlier arrival
      RR       -> arrivals during a slice enter the queue before the
                  preempted process is put back."""
    n = len(procs)
    segs, info = [], {}

    def finish(p, ct, start):
        info[p["pid"]] = {"start": start, "ct": ct,
                          "tat": ct - p["at"],
                          "wt": ct - p["at"] - p["bt"]}

    if algo != "RR":
        pool = sorted(procs, key=lambda p: p["at"]) if algo == "FCFS" else list(procs)
        done, t = set(), 0
        while len(done) < n:
            avail = [p for p in pool if p["pid"] not in done and p["at"] <= t]
            if not avail:
                nxt = min(p["at"] for p in pool if p["pid"] not in done)
                segs.append((None, t, nxt))
                t = nxt
                continue
            if algo == "FCFS":
                p = avail[0]
            elif algo == "SJF":
                p = min(avail, key=lambda x: (x["bt"], x["at"]))
            else:
                p = min(avail, key=lambda x: (x["pr"], x["at"]))
            segs.append((p["pid"], t, t + p["bt"]))
            finish(p, t + p["bt"], t)
            t += p["bt"]
            done.add(p["pid"])
        return segs, info

    # ----- Round Robin
    rem = {p["pid"]: p["bt"] for p in procs}
    byid = {p["pid"]: p for p in procs}
    first, queue, inq = {}, deque(), set()
    t, completed = 0, 0

    def admit(skip=None):
        for p in procs:
            q = p["pid"]
            if q != skip and rem[q] > 0 and q not in inq and p["at"] <= t:
                queue.append(q)
                inq.add(q)

    admit()
    while completed < n:
        if not queue:
            nxt = min(p["at"] for p in procs if rem[p["pid"]] > 0)
            if nxt > t:
                segs.append((None, t, nxt))
            t = nxt
            admit()
        idx = queue.popleft()
        inq.discard(idx)
        run = min(quantum, rem[idx])
        first.setdefault(idx, t)
        segs.append((idx, t, t + run))
        t += run
        rem[idx] -= run
        admit(skip=idx)
        if rem[idx] == 0:
            finish(byid[idx], t, first[idx])
            completed += 1
        else:
            queue.append(idx)
            inq.add(idx)
    return segs, info


# --------------------------------------------------------------- widgets
class RButton(tk.Canvas):
    """Rounded, glossy, animated button."""

    def __init__(self, parent, text, command, color=None,
                 width=110, height=36, size=10, bg=None):
        super().__init__(parent, width=width, height=height, bg=bg or T.card,
                         highlightthickness=0, cursor="hand2")
        self.w, self.h, self.size = width, height, size
        self.text, self.cmd, self.color = text, command, color or T.accent
        self.hover = self.down = False
        self.bind("<Enter>", lambda e: self._set(hover=True))
        self.bind("<Leave>", lambda e: self._set(hover=False, down=False))
        self.bind("<ButtonPress-1>", lambda e: self._set(down=True))
        self.bind("<ButtonRelease-1>", self._release)
        self.draw()

    def _set(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.draw()

    def _release(self, e):
        was = self.down
        self._set(down=False)
        if was and 0 <= e.x <= self.w and 0 <= e.y <= self.h:
            self.cmd()

    def set_text(self, t):
        self.text = t
        self.draw()

    def draw(self):
        self.delete("all")
        col = lighten(self.color, 0.16) if self.hover else self.color
        if self.down:
            col = darken(self.color, 0.15)
        off = 2 if self.down else 0
        rrect(self, 1, 3, self.w - 1, self.h - 1, 12, fill=darken(col, 0.5), outline="")
        rrect(self, 1, 1 + off, self.w - 1, self.h - 3 + off, 12, fill=col, outline="")
        rrect(self, 4, 3 + off, self.w - 4, self.h * 0.46 + off, 9,
              fill=lighten(col, 0.16), outline="")
        self.create_text(self.w / 2, (self.h - 2) / 2 + off, text=self.text,
                         fill=ink(col), font=("Segoe UI", self.size, "bold"))


class Segmented(tk.Canvas):
    """Pill toggle bound to a StringVar."""

    def __init__(self, parent, options, variable, width=330, height=40,
                 size=10, bg=None):
        super().__init__(parent, width=width, height=height, bg=bg or T.card,
                         highlightthickness=0, cursor="hand2")
        self.options, self.var = options, variable
        self.w, self.h, self.size = width, height, size
        self.bind("<Button-1>", self.click)
        self._tid = variable.trace_add("write", lambda *a: self._safe_draw())
        self.draw()

    def _safe_draw(self):
        try:
            self.draw()
        except tk.TclError:
            pass

    def destroy(self):
        try:
            self.var.trace_remove("write", self._tid)
        except Exception:
            pass
        super().destroy()

    def click(self, e):
        i = min(len(self.options) - 1, int(e.x / (self.w / len(self.options))))
        self.var.set(self.options[i][1])

    def draw(self):
        self.delete("all")
        rrect(self, 1, 1, self.w - 1, self.h - 1, self.h / 2 - 1,
              fill=T.card2, outline=T.border)
        seg = self.w / len(self.options)
        for i, (label, val) in enumerate(self.options):
            active = self.var.get() == val
            if active:
                rrect(self, i * seg + 4, 4, (i + 1) * seg - 4, self.h - 4,
                      self.h / 2 - 4, fill=T.accent, outline=lighten(T.accent, 0.3))
            self.create_text(i * seg + seg / 2, self.h / 2, text=label,
                             fill=ink(T.accent) if active else T.muted,
                             font=("Segoe UI", self.size, "bold"))


# ------------------------------------------------------------------- app
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        set_theme("Aurora")
        self.title("Mini OS Scheduling Simulator")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1360, sw - 20), min(800, sh - 70)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - 20)}")
        self.minsize(1180, 660)
        self.configure(bg=T.bg)
        self.bind("<F5>", lambda e: self.run())

        self.procs, self.cmap = [], {}
        self.segs, self.info = [], {}
        self.t = 0.0
        self.running = self.finished = False
        self.after_id = None
        self.last = time.time()
        self.run_id = 0
        self.shown_rows = set()
        self.sparks = []
        self.stats = None
        self.count = 0.0
        self.waves, self.stars = [], []
        self.run_algo, self.run_quantum = "FCFS", 2
        self.hover, self.hx, self.hy = None, 0, 0
        self.toast_w = None
        self.cmp_data, self.cmp_k = None, 1.0

        self.algo = tk.StringVar(value="FCFS")
        self.quantum = tk.StringVar(value="2")
        self.speed = tk.DoubleVar(value=3.0)
        self.status = tk.StringVar(value="Ready")
        self.view = tk.StringVar(value="results")
        self.v = {k: tk.StringVar() for k in ("pid", "at", "bt", "pr")}
        self.v["pr"].set("1")
        self.algo.trace_add("write", lambda *a: self.draw())
        self.view.trace_add("write", lambda *a: self.show_view())

        self.load_sample()
        self.build_all()
        self.anim()

    # ------------------------------------------------------ (re)build
    def build_all(self):
        for w in self.winfo_children():
            w.destroy()
        self.toast_w = None
        self.setup_style()
        self.build_ui()
        self.refresh_input()
        self.refresh_results()
        self.show_view()
        self.draw()

    def apply_theme(self, name):
        if name == T.name:
            return
        set_theme(name)
        self.configure(bg=T.bg)
        self.build_all()
        self.toast(f"{name} theme", "info")

    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=T.card2, fieldbackground=T.card2,
                    foreground=T.fg, rowheight=28, borderwidth=0,
                    font=("Segoe UI", 10))
        s.configure("Treeview.Heading", background=T.card, foreground=T.accent2,
                    font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        s.map("Treeview", background=[("selected", blend(T.accent, T.card2, .65))],
              foreground=[("selected", T.fg)])
        s.map("Treeview.Heading", background=[("active", T.card)])
        s.configure("Horizontal.TScale", background=T.accent, troughcolor=T.card2)
        s.configure("Vertical.TScrollbar", background=T.card2, troughcolor=T.card,
                    bordercolor=T.card, arrowcolor=T.muted,
                    lightcolor=T.card2, darkcolor=T.card2)

    def card(self, parent):
        return tk.Frame(parent, bg=T.card, highlightbackground=T.border,
                        highlightthickness=1)

    def section(self, parent, text, color):
        f = tk.Frame(parent, bg=T.card)
        f.pack(fill="x", padx=16, pady=(12, 6))
        tk.Frame(f, bg=color, width=4, height=16).pack(side="left", padx=(0, 8))
        tk.Label(f, text=text, bg=T.card, fg=T.fg,
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        return f

    def vsep(self, parent):
        tk.Frame(parent, bg=T.border, width=1, height=28).pack(side="left", padx=12)

    def entry(self, parent, var, width):
        return tk.Entry(parent, textvariable=var, width=width, bg=T.card2, fg=T.fg,
                        insertbackground=T.fg, relief="flat",
                        highlightthickness=1, highlightbackground=T.border,
                        highlightcolor=T.accent, font=("Segoe UI", 12),
                        justify="center")

    # -------------------------------------------------------------- UI
    def build_ui(self):
        # ---- header
        self.header = tk.Canvas(self, height=72, bg=T.bg, highlightthickness=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self.draw_header)

        # ---- toolbar
        tb = self.card(self)
        tb.pack(fill="x", padx=16, pady=(10, 0))
        bar = tk.Frame(tb, bg=T.card)
        bar.pack(fill="x", padx=12, pady=8)
        RButton(bar, "📊 Compare", self.compare, T.pink, 114, 40).pack(side="right")
        RButton(bar, "▶  RUN", self.run, T.accent, 108, 40).pack(side="left")
        self.b_pause = RButton(bar, "⏸ Pause", self.toggle_pause, T.accent2, 98, 40)
        self.b_pause.pack(side="left", padx=6)
        RButton(bar, "⏭ Step", self.step, T.neutral, 88, 40).pack(side="left")
        RButton(bar, "↺ Reset", self.reset, T.neutral, 92, 40).pack(side="left", padx=6)
        self.vsep(bar)
        Segmented(bar, [("FCFS", "FCFS"), ("SJF", "SJF"), ("Priority", "PRIORITY"),
                        ("R. Robin", "RR")], self.algo, 320, 40, size=9).pack(side="left")
        self.vsep(bar)
        tk.Label(bar, text="Quantum", bg=T.card, fg=T.muted,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        RButton(bar, "−", lambda: self.step_q(-1), T.neutral, 30, 30, 12).pack(side="left")
        self.q_entry = self.entry(bar, self.quantum, 4)
        self.q_entry.pack(side="left", padx=5, ipady=3)
        RButton(bar, "+", lambda: self.step_q(1), T.neutral, 30, 30, 12).pack(side="left")
        self.vsep(bar)
        sp = tk.Frame(bar, bg=T.card)
        sp.pack(side="left", fill="x", expand=True)
        tk.Label(sp, text="🐢", bg=T.card, fg=T.fg).pack(side="left")
        ttk.Scale(sp, from_=1, to=20, variable=self.speed).pack(
            side="left", fill="x", expand=True, padx=6)
        tk.Label(sp, text="🐇", bg=T.card, fg=T.fg).pack(side="left")

        main = tk.Frame(self, bg=T.bg)
        main.pack(fill="both", expand=True, padx=16, pady=(10, 14))

        # ---------------- left: process manager
        left = self.card(main)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=384)
        left.pack_propagate(False)
        self.section(left, "PROCESS MANAGER", T.accent)

        form = tk.Frame(left, bg=T.card)
        form.pack(fill="x", padx=16)
        self.entries = {}
        for i, (lbl, key) in enumerate([("PID", "pid"), ("Arrival", "at"),
                                        ("Burst", "bt"), ("Priority", "pr")]):
            tk.Label(form, text=lbl, bg=T.card, fg=T.muted,
                     font=("Segoe UI", 9)).grid(row=0, column=i, sticky="w")
            e = self.entry(form, self.v[key], 6)
            e.grid(row=1, column=i, padx=(0, 8), pady=(2, 0), ipady=6)
            e.bind("<Return>", lambda ev: self.add_process())
            self.entries[key] = e
        tk.Label(left, text="PID blank = auto  ·  Priority 1 = highest",
                 bg=T.card, fg=T.dim, font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(4, 6))

        for row in ([("+ Add", self.add_process, T.good),
                     ("✎ Update", self.update_process, T.accent2),
                     ("✕ Delete", self.delete_process, T.bad)],
                    [("🔍 Search", self.search_process, T.accent),
                     ("💾 Save", self.save_processes, T.warn),
                     ("📂 Load", self.load_processes, T.pink)],
                    [("🎲 Random", self.load_random, T.neutral),
                     ("🧹 Clear", self.clear_all, T.neutral)]):
            f = tk.Frame(left, bg=T.card)
            f.pack(fill="x", padx=16, pady=2)
            for text, cmd, colr in row:
                RButton(f, text, cmd, colr, 108, 34, 9).pack(side="left", padx=(0, 8))

        wrap = tk.Frame(left, bg=T.card)
        wrap.pack(fill="both", expand=True, padx=16, pady=(10, 14))
        cols = ("pid", "at", "bt", "pr")
        self.tree_in = ttk.Treeview(wrap, columns=cols, show="headings",
                                    selectmode="browse")
        for c, h in zip(cols, ("PID", "Arrival", "Burst", "Priority")):
            self.tree_in.heading(c, text=h)
            self.tree_in.column(c, width=70, anchor="center")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree_in.yview)
        self.tree_in.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree_in.pack(side="left", fill="both", expand=True)
        self.tree_in.bind("<<TreeviewSelect>>", self.on_select)

        # ---------------- right: visual area
        right = tk.Frame(main, bg=T.bg)
        right.pack(side="left", fill="both", expand=True)

        self.hud = tk.Canvas(right, height=98, bg=T.bg, highlightthickness=0)
        self.hud.pack(fill="x")
        self.hud.bind("<Configure>", lambda e: self.draw_hud())

        self.gantt = tk.Canvas(right, height=232, bg=T.bg, highlightthickness=0)
        self.gantt.pack(fill="x", pady=(8, 8))
        self.gantt.bind("<Configure>", lambda e: self.draw_gantt())
        self.gantt.bind("<Motion>", self.on_gantt_move)
        self.gantt.bind("<Leave>", self.on_gantt_leave)

        bottom = tk.Frame(right, bg=T.bg)
        bottom.pack(fill="both", expand=True)

        rc = self.card(bottom)
        rc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        head = tk.Frame(rc, bg=T.card)
        head.pack(fill="x", padx=16, pady=(10, 6))
        tk.Frame(head, bg=T.good, width=4, height=16).pack(side="left", padx=(0, 8))
        self.view_title = tk.Label(head, text="RESULTS", bg=T.card, fg=T.fg,
                                   font=("Segoe UI", 11, "bold"))
        self.view_title.pack(side="left")
        Segmented(head, [("Results", "results"), ("Compare", "compare")],
                  self.view, 200, 30, size=9).pack(side="right")

        self.tree_wrap = tk.Frame(rc, bg=T.card)
        cols = ("pid", "at", "bt", "pr", "ct", "tat", "wt")
        self.tree_out = ttk.Treeview(self.tree_wrap, columns=cols, show="headings")
        for c, h in zip(cols, ("PID", "AT", "BT", "PR", "CT", "TAT", "WT")):
            self.tree_out.heading(c, text=h)
            self.tree_out.column(c, width=56, anchor="center")
        sb2 = ttk.Scrollbar(self.tree_wrap, orient="vertical",
                            command=self.tree_out.yview)
        self.tree_out.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self.tree_out.pack(side="left", fill="both", expand=True)

        self.cmp = tk.Canvas(rc, bg=T.card, highlightthickness=0)
        self.cmp.bind("<Configure>", lambda e: self.draw_compare())

        self.statc = tk.Canvas(bottom, width=372, height=178, bg=T.bg,
                               highlightthickness=0)
        self.statc.pack(side="left", fill="y")

    def show_view(self):
        try:
            if self.view.get() == "results":
                self.cmp.pack_forget()
                self.tree_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 14))
                self.view_title.config(text="RESULTS")
            else:
                self.tree_wrap.pack_forget()
                self.cmp.pack(fill="both", expand=True, padx=16, pady=(0, 10))
                self.view_title.config(text="ALGORITHM COMPARISON  ·  avg waiting time")
                self.draw_compare()
        except (AttributeError, tk.TclError):
            pass

    # ---------------------------------------------------------- header
    def draw_header(self, e=None):
        c = self.header
        c.delete("all")
        W, H = max(c.winfo_width(), 900), 72
        for x in range(0, W, 4):
            c.create_rectangle(x, 0, x + 4, H,
                               fill=blend(T.hdr1, T.hdr2, x / W), outline="")
        mid = blend(T.hdr1, T.hdr2, .5)
        self.waves = [c.create_line(0, 0, 10, 10, fill=lighten(mid, .12 + .1 * i),
                                    width=2, smooth=True) for i in range(3)]
        self.stars = []
        for _ in range(26):
            x, y = random.randint(0, W), random.randint(4, H - 8)
            r = random.choice([1, 1, 2])
            it = c.create_oval(x, y, x + r * 2, y + r * 2, fill="#ffffff", outline="")
            self.stars.append([it, random.uniform(0.2, 0.8), random.random() * 6])
        rrect(c, 22, 14, 66, 58, 13, fill="#ffffff", outline="")
        c.create_text(44, 36, text="⚙", fill=T.hdr1, font=("Segoe UI", 22, "bold"))
        c.create_text(80, 28, anchor="w", text="Mini OS Scheduling Simulator",
                      fill="#ffffff", font=("Segoe UI", 19, "bold"))
        c.create_text(82, 53, anchor="w", fill=T.hsub, font=("Segoe UI", 9, "bold"),
                      text="FCFS  •  SJF  •  Priority  •  Round Robin   —   "
                           "live Gantt chart, compare, save & load")
        x = W - 26
        for name in reversed(list(THEMES)):
            active = name == T.name
            it = c.create_oval(x - 12, 24, x + 12, 48, fill=THEMES[name]["accent"],
                               outline="#ffffff" if active else THEMES[name]["hdr2"],
                               width=3 if active else 2)
            c.tag_bind(it, "<Button-1>",
                       lambda ev, n=name: self.after(10, lambda: self.apply_theme(n)))
            c.tag_bind(it, "<Enter>", lambda ev: c.config(cursor="hand2"))
            c.tag_bind(it, "<Leave>", lambda ev: c.config(cursor=""))
            x -= 32
        c.create_text(x + 8, 36, anchor="e", text="THEME", fill=T.hsub,
                      font=("Segoe UI", 8, "bold"))

    def anim(self):
        try:
            c = self.header
            W = max(c.winfo_width(), 900)
            now = time.time()
            for i, it in enumerate(self.waves):
                pts = []
                for x in range(0, W + 20, 20):
                    y = (36 + math.sin(x / 110 + now * (0.9 + 0.3 * i) + i * 2) * (10 + 4 * i)
                         + math.sin(x / 47 - now * 0.7) * 3)
                    pts += [x, y]
                c.coords(it, *pts)
            mid = blend(T.hdr1, T.hdr2, .5)
            for s in self.stars:
                c.move(s[0], -s[1], 0)
                co = c.coords(s[0])
                if co and co[2] < 0:
                    c.move(s[0], W + 10, 0)
                tw = (math.sin(now * 2 + s[2]) + 1) / 2
                c.itemconfig(s[0], fill=blend(mid, "#ffffff", tw))
        except tk.TclError:
            pass
        self.after(40, self.anim)

    # ------------------------------------------------------------ toast
    def toast(self, msg, kind="info"):
        col = {"info": T.accent2, "good": T.good, "bad": T.bad, "warn": T.warn}[kind]
        if self.toast_w is not None:
            try:
                self.toast_w.destroy()
            except tk.TclError:
                pass
        w = tk.Label(self, text=msg, bg=col, fg=ink(col), padx=16, pady=9,
                     font=("Segoe UI", 10, "bold"))
        self.toast_w = w
        w.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=50)
        w.lift()
        self._slide(w, 50.0)
        self.after(3000, lambda: self._drop(w))

    def _slide(self, w, y):
        try:
            if not w.winfo_exists():
                return
            y -= (y + 24) * 0.28
            w.place_configure(y=y)
            if y > -23:
                self.after(16, lambda: self._slide(w, y))
        except tk.TclError:
            pass

    def _drop(self, w):
        try:
            if w.winfo_exists():
                w.destroy()
        except tk.TclError:
            pass
        if self.toast_w is w:
            self.toast_w = None

    # ------------------------------------------------------ colours
    def col(self, pid):
        if pid not in self.cmap:
            used = {self.cmap[p["pid"]] for p in self.procs if p["pid"] in self.cmap}
            free = [c for c in COLORS if c not in used]
            self.cmap[pid] = free[0] if free else COLORS[pid % len(COLORS)]
        return self.cmap[pid]

    # ------------------------------------------------- process manager
    def refresh_input(self):
        self.tree_in.delete(*self.tree_in.get_children())
        for p in self.procs:
            self.tree_in.tag_configure(f"p{p['pid']}", foreground=self.col(p["pid"]))
            self.tree_in.insert("", "end", iid=str(p["pid"]), tags=(f"p{p['pid']}",),
                                values=(f"P{p['pid']}", p["at"], p["bt"], p["pr"]))

    def refresh_results(self):
        self.tree_out.delete(*self.tree_out.get_children())
        for pid, d in sorted(self.info.items(), key=lambda kv: kv[1]["ct"]):
            if pid in self.shown_rows:
                self.insert_row(pid, d)

    def insert_row(self, pid, d):
        p = next(x for x in self.procs if x["pid"] == pid)
        self.tree_out.tag_configure(f"p{pid}", foreground=self.col(pid))
        self.tree_out.insert("", "end", tags=(f"p{pid}",),
                             values=(f"P{pid}", p["at"], p["bt"], p["pr"],
                                     d["ct"], d["tat"], d["wt"]))
        self.tree_out.yview_moveto(1)

    def changed(self):
        """Process list was edited: drop old run + comparison."""
        self.cmp_data = None
        self.reset()

    def field(self, key, label, lo, blank_ok=False):
        s = self.v[key].get().strip()
        if s == "":
            if blank_ok:
                return None
            raise ValueError(f"{label} is required.")
        try:
            x = int(s)
        except ValueError:
            raise ValueError(f"{label} must be an integer.")
        if not lo <= x <= LIMIT:
            raise ValueError(f"{label} must be between {lo} and {LIMIT}.")
        return x

    def find(self, pid):
        for i, p in enumerate(self.procs):
            if p["pid"] == pid:
                return i
        return -1

    def target_pid(self):
        s = self.v["pid"].get().strip()
        if s.isdigit() and self.find(int(s)) != -1:
            return int(s)
        sel = self.tree_in.selection()
        return int(sel[0]) if sel else None

    def on_select(self, e=None):
        sel = self.tree_in.selection()
        if not sel:
            return
        p = self.procs[self.find(int(sel[0]))]
        self.v["pid"].set(str(p["pid"]))
        self.v["at"].set(str(p["at"]))
        self.v["bt"].set(str(p["bt"]))
        self.v["pr"].set(str(p["pr"]))

    def add_process(self):
        if len(self.procs) >= MAX:
            self.toast(f"Process limit reached! (max {MAX})", "warn")
            return
        try:
            pid = self.field("pid", "Process ID", 1, blank_ok=True)
            at = self.field("at", "Arrival time", 0)
            bt = self.field("bt", "Burst time", 1)
            pr = self.field("pr", "Priority", 1)
        except ValueError as ex:
            self.toast(str(ex), "bad")
            return
        if pid is None:
            pid = 1
            while self.find(pid) != -1:
                pid += 1
        elif self.find(pid) != -1:
            self.toast("This Process ID already exists!", "bad")
            return
        self.procs.append({"pid": pid, "at": at, "bt": bt, "pr": pr})
        self.col(pid)
        for k in ("pid", "at", "bt"):
            self.v[k].set("")
        self.entries["at"].focus_set()
        self.refresh_input()
        self.changed()
        self.tree_in.selection_remove(*self.tree_in.selection())
        self.toast(f"P{pid} added", "good")

    def update_process(self):
        pid = self.target_pid()
        if pid is None:
            self.toast("Select a process (or type its PID) first.", "warn")
            return
        try:
            at = self.field("at", "Arrival time", 0, True)
            bt = self.field("bt", "Burst time", 1, True)
            pr = self.field("pr", "Priority", 1, True)
        except ValueError as ex:
            self.toast(str(ex), "bad")
            return
        p = self.procs[self.find(pid)]
        if at is not None:
            p["at"] = at
        if bt is not None:
            p["bt"] = bt
        if pr is not None:
            p["pr"] = pr
        self.refresh_input()
        self.tree_in.selection_set(str(pid))
        self.changed()
        self.toast(f"P{pid} updated successfully!", "good")

    def delete_process(self):
        if not self.procs:
            self.toast("No processes to delete.", "warn")
            return
        pid = self.target_pid()
        if pid is None:
            self.toast("Select a process (or type its PID) first.", "warn")
            return
        del self.procs[self.find(pid)]
        self.cmap.pop(pid, None)
        for k in ("pid", "at", "bt"):
            self.v[k].set("")
        self.refresh_input()
        self.changed()
        self.toast(f"P{pid} deleted", "good")

    def search_process(self):
        if not self.procs:
            self.toast("No processes available.", "warn")
            return
        try:
            pid = self.field("pid", "Process ID", 1)
        except ValueError as ex:
            self.toast(str(ex), "bad")
            return
        arr = sorted(self.procs, key=lambda p: p["pid"])
        idx, steps = binary_search(arr, 0, len(arr) - 1, pid)
        if idx == -1:
            self.toast("Process not found!", "bad")
            return
        p = arr[idx]
        self.tree_in.selection_set(str(pid))
        self.tree_in.see(str(pid))
        self.toast(f"Found P{pid}:  AT {p['at']}  BT {p['bt']}  PR {p['pr']}"
                   f"   (binary search, {steps} step{'s' if steps != 1 else ''})", "good")

    def save_processes(self):
        try:
            with open(SAVE_FILE, "w") as f:
                f.write(f"{len(self.procs)}\n")
                for p in self.procs:
                    f.write(f"{p['pid']} {p['at']} {p['bt']} {p['pr']}\n")
        except OSError as ex:
            self.toast(f"Could not save file: {ex.strerror}", "bad")
            return
        self.toast(f"Processes saved in processes.txt successfully!", "good")

    def load_processes(self):
        try:
            with open(SAVE_FILE) as f:
                tok = f.read().split()
        except OSError as ex:
            self.toast(f"Could not open file: {ex.strerror}", "bad")
            return
        try:
            nums = [int(x) for x in tok]
        except ValueError:
            self.toast("File data is incomplete or damaged.", "bad")
            return
        if not nums or nums[0] < 0 or nums[0] > MAX:
            self.toast("File data is not valid.", "bad")
            return
        count = nums[0]
        if len(nums) < 1 + 4 * count:
            self.toast("File data is incomplete or damaged.", "bad")
            return
        new, seen = [], set()
        for i in range(count):
            pid, at, bt, pr = nums[1 + 4 * i: 5 + 4 * i]
            if pid <= 0 or at < 0 or bt <= 0 or pr <= 0:
                self.toast("File contains invalid process values.", "bad")
                return
            if pid in seen:
                self.toast("File contains duplicate Process IDs.", "bad")
                return
            seen.add(pid)
            new.append({"pid": pid, "at": at, "bt": bt, "pr": pr})
        self.procs, self.cmap = new, {}
        self.refresh_input()
        self.changed()
        self.toast(f"{count} processes loaded successfully!", "good")

    def clear_all(self):
        self.procs, self.cmap = [], {}
        for k in ("pid", "at", "bt"):
            self.v[k].set("")
        self.refresh_input()
        self.changed()

    def load_sample(self):
        data = [(0, 6, 2), (2, 8, 1), (4, 3, 3), (20, 4, 2)]   # includes an idle gap
        self.procs = [{"pid": i + 1, "at": a, "bt": b, "pr": p}
                      for i, (a, b, p) in enumerate(data)]
        self.cmap = {}

    def load_random(self):
        n = random.randint(4, 7)
        self.procs = [{"pid": i + 1, "at": random.randint(0, 10),
                       "bt": random.randint(1, 9), "pr": random.randint(1, 5)}
                      for i in range(n)]
        self.cmap = {}
        self.refresh_input()
        self.changed()
        self.toast(f"{n} random processes generated", "info")

    # ------------------------------------------------ algorithm helpers
    def step_q(self, d):
        try:
            q = int(self.quantum.get())
        except ValueError:
            q = 2
        self.quantum.set(str(max(1, min(LIMIT, q + d))))

    def read_quantum(self):
        try:
            q = int(self.quantum.get().strip())
            if not 1 <= q <= LIMIT:
                raise ValueError
            return q
        except ValueError:
            self.toast(f"Time Quantum must be an integer from 1 to {LIMIT}.", "bad")
            return None

    def slices_ok(self, q):
        slices = sum(-(-p["bt"] // q) for p in self.procs)
        if slices > MAX_SLICES:
            self.toast(f"That makes {slices} time slices - increase the Time Quantum.", "warn")
            return False
        return True

    # ------------------------------------------------------- animation
    def prepare(self):
        if not self.procs:
            self.toast("Add at least one process first.", "warn")
            return False
        algo, q = self.algo.get(), 2
        if algo == "RR":
            q = self.read_quantum()
            if q is None or not self.slices_ok(q):
                return False
        self.reset()
        self.run_algo, self.run_quantum = algo, q
        self.segs, self.info = schedule(self.procs, algo, q)
        self.t = 0.0
        return True

    def run(self):
        if not self.prepare():
            return
        self.view.set("results")
        self.running = True
        self.status.set(f"{ALGO_NAMES[self.run_algo]} running…")
        self.b_pause.set_text("⏸ Pause")
        self.last = time.time()
        self.tick()

    def step(self):
        if not self.segs or self.finished:
            if not self.prepare():
                return
            self.view.set("results")
        if self.running:
            self.running = False
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None
        total = self.segs[-1][2]
        bounds = sorted({e for _, _, e in self.segs})
        nxt = next((b for b in bounds if b > self.t + 1e-9), total)
        self.status.set("Stepping")
        self.b_pause.set_text("▶ Resume")
        self.advance(float(nxt))

    def toggle_pause(self):
        if not self.segs or self.finished:
            return
        self.running = not self.running
        if self.running:
            self.b_pause.set_text("⏸ Pause")
            self.status.set(f"{ALGO_NAMES[self.run_algo]} running…")
            self.last = time.time()
            self.tick()
        else:
            self.b_pause.set_text("▶ Resume")
            self.status.set("Paused")
            self.draw()

    def reset(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.run_id += 1
        self.running = self.finished = False
        self.segs, self.info = [], {}
        self.t, self.count, self.stats = 0.0, 0.0, None
        self.sparks, self.hover = [], None
        self.shown_rows = set()
        try:
            self.tree_out.delete(*self.tree_out.get_children())
            self.b_pause.set_text("⏸ Pause")
        except tk.TclError:
            pass
        self.status.set("Ready")
        self.draw()

    def tick(self):
        if not self.running:
            return
        now = time.time()
        total = self.segs[-1][2]
        rate = self.speed.get() * max(1.0, total / 50)      # long runs stay watchable
        nt = self.t + (now - self.last) * rate
        self.last = now
        self.advance(nt)
        if self.running:
            self.after_id = self.after(16, self.tick)

    def advance(self, nt):
        total = self.segs[-1][2]
        self.t = min(float(total), nt)
        self.update_rows()
        if self.t >= total and not self.finished:
            self.finish()
        self.draw()

    def update_rows(self):
        for pid, d in sorted(self.info.items(), key=lambda kv: kv[1]["ct"]):
            if d["ct"] <= self.t and pid not in self.shown_rows:
                self.shown_rows.add(pid)
                self.insert_row(pid, d)

    def finish(self):
        self.finished, self.running = True, False
        n = len(self.procs)
        total = self.segs[-1][2]
        busy = sum(p["bt"] for p in self.procs)
        self.stats = {
            "wt": sum(d["wt"] for d in self.info.values()) / n,
            "tat": sum(d["tat"] for d in self.info.values()) / n,
            "util": busy / total * 100,
            "thr": n / total,
        }
        self.status.set(f"{ALGO_NAMES[self.run_algo]} completed ✔")
        self.b_pause.set_text("⏸ Pause")
        W = max(self.gantt.winfo_width(), 700)
        for _ in range(60):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(2, 7)
            self.sparks.append([W - 36, 120, math.cos(ang) * sp,
                                math.sin(ang) * sp - 2, random.randint(30, 60),
                                random.choice(COLORS)])
        self.count = 0.0
        self.after(16, lambda: self.finish_loop(self.run_id))
        self.toast(f"{ALGO_NAMES[self.run_algo]} done  ·  avg WT {self.stats['wt']:.2f}"
                   f"  ·  avg TAT {self.stats['tat']:.2f}", "good")

    def finish_loop(self, rid):
        if rid != self.run_id:
            return
        self.count = min(1.0, self.count + 0.025)
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[3] += 0.22
            s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]
        self.draw()
        if self.count < 1.0 or self.sparks:
            self.after(16, lambda: self.finish_loop(rid))

    # ---------------------------------------------------------- compare
    def compare(self):
        if not self.procs:
            self.toast("No processes available.", "warn")
            return
        q = self.read_quantum()
        if q is None or not self.slices_ok(q):
            return
        n = len(self.procs)
        rows = []
        for key, colr in (("FCFS", T.accent), ("SJF", T.accent2),
                          ("PRIORITY", T.pink), ("RR", T.warn)):
            _, info = schedule(self.procs, key, q)
            rows.append({"name": ALGO_NAMES[key], "color": colr,
                         "wt": sum(d["wt"] for d in info.values()) / n,
                         "tat": sum(d["tat"] for d in info.values()) / n})
        self.cmp_data, self.cmp_k = rows, 0.0
        self.view.set("compare")
        best = min(rows, key=lambda r: r["wt"])
        self.toast(f"Best average waiting time: {best['name']} ({best['wt']:.2f})", "good")
        self.cmp_loop()

    def cmp_loop(self):
        self.cmp_k = min(1.0, self.cmp_k + 0.04)
        self.draw_compare()
        if self.cmp_k < 1.0:
            self.after(16, self.cmp_loop)

    def draw_compare(self):
        c = self.cmp
        try:
            c.delete("all")
            W, H = max(c.winfo_width(), 420), max(c.winfo_height(), 130)
        except tk.TclError:
            return
        if not self.cmp_data:
            c.create_text(W / 2, H / 2, fill=T.muted, font=("Segoe UI", 12, "bold"),
                          text="Press  📊 Compare  to run all four algorithms")
            return
        rows = self.cmp_data
        best = min(r["wt"] for r in rows)
        maxv = max(max(r["wt"] for r in rows), 1e-9)
        k = 1 - (1 - self.cmp_k) ** 3
        left, right = 120, W - 120
        rh = (H - 10) / len(rows)
        for i, r in enumerate(rows):
            y = 6 + i * rh
            cy = y + rh / 2
            is_best = abs(r["wt"] - best) < 1e-9
            c.create_text(6, cy - 6, anchor="w", text=r["name"], fill=T.fg,
                          font=("Segoe UI", 10, "bold"))
            c.create_text(6, cy + 8, anchor="w", text=f"TAT {r['tat']:.2f}",
                          fill=T.muted, font=("Segoe UI", 8))
            rrect(c, left, cy - 9, right, cy + 9, 9, fill=T.card2, outline="")
            w = (right - left) * r["wt"] / maxv * k
            if w > 3:
                rrect(c, left, cy - 9, left + w, cy + 9, 9, fill=r["color"],
                      outline=lighten(r["color"], .5) if is_best else "")
            txt = f"{r['wt'] * k:.2f}" + ("  ★ best" if is_best and k > .95 else "")
            c.create_text(right + 10, cy, anchor="w", text=txt,
                          fill=T.good if is_best else T.fg,
                          font=("Segoe UI", 10, "bold"))

    # ------------------------------------------------------------ draw
    def current(self):
        """('idle'|'run'|'done'|'none', pid)"""
        if not self.segs:
            return ("none", None)
        if self.t >= self.segs[-1][2]:
            return ("done", None)
        for pid, s, e in self.segs:
            if s <= self.t < e:
                return ("idle", None) if pid is None else ("run", pid)
        return ("idle", None)

    def draw(self):
        try:
            self.draw_hud()
            self.draw_gantt()
            self.draw_stats()
        except (AttributeError, tk.TclError):
            pass

    def draw_hud(self):
        c = self.hud
        c.delete("all")
        W, H = max(c.winfo_width(), 700), 98
        kind, pid = self.current()
        total = self.segs[-1][2] if self.segs else 0
        algo = self.run_algo if self.segs else self.algo.get()

        # clock
        rrect(c, 2, 2, 230, H - 2, 18, fill=T.card, outline=T.border)
        c.create_text(22, 22, anchor="w", text="CLOCK", fill=T.muted,
                      font=("Segoe UI", 9, "bold"))
        c.create_text(22, 50, anchor="w", text=f"{self.t:7.1f}", fill=T.accent2,
                      font=("Consolas", 26, "bold"))
        c.create_text(172, 58, anchor="w", text="units", fill=T.muted,
                      font=("Segoe UI", 9))
        rrect(c, 22, H - 20, 210, H - 12, 4, fill=T.card2, outline="")
        if total and self.t / total > 0.02:
            frac = self.t / total
            rrect(c, 22, H - 20, 22 + 188 * frac, H - 12, 4,
                  fill=blend(T.accent, T.accent2, frac), outline="")

        # cpu
        rrect(c, 242, 2, 490, H - 2, 18, fill=T.card, outline=T.border)
        c.create_text(262, 22, anchor="w", text="CPU", fill=T.muted,
                      font=("Segoe UI", 9, "bold"))
        cx, cy = 312, 58
        if kind == "run":
            col, label, sub = self.col(pid), f"P{pid}", "EXECUTING"
        elif kind == "idle":
            col, label, sub = T.dim, "—", "IDLE"
        elif kind == "done":
            col, label, sub = T.good, "✔", "FINISHED"
        else:
            col, label, sub = T.dim, "·", "STANDBY"
        pulse = (math.sin(time.time() * 6) + 1) / 2 if kind == "run" else 0
        for r, m in ((34, .88), (30, .78), (26, .6)):
            rr = r + pulse * 4
            c.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                          fill=blend(col, T.card, m), outline="")
        c.create_oval(cx - 22, cy - 22, cx + 22, cy + 22, fill=col,
                      outline=lighten(col, .4), width=2)
        c.create_text(cx, cy, text=label, fill=INK,
                      font=("Segoe UI", 14 if len(label) < 4 else 11, "bold"))
        c.create_text(358, 48, anchor="w", text=sub, fill=col,
                      font=("Segoe UI", 12, "bold"))
        extra = f"  ·  Q = {self.run_quantum}" if (algo == "RR" and self.segs) else ""
        c.create_text(358, 68, anchor="w", text=ALGO_NAMES[algo] + extra,
                      fill=T.muted, font=("Segoe UI", 9))

        # ready queue
        rrect(c, 502, 2, W - 2, H - 2, 18, fill=T.card, outline=T.border)
        c.create_text(522, 22, anchor="w", text="READY QUEUE", fill=T.muted,
                      font=("Segoe UI", 9, "bold"))
        run_pid = pid if kind == "run" else None
        waiting = [p["pid"] for p in self.procs
                   if p["pid"] in self.info and p["at"] <= self.t
                   and self.info[p["pid"]]["ct"] > self.t and p["pid"] != run_pid]
        waiting.sort(key=self.next_start)
        if not waiting:
            c.create_text(522, 60, anchor="w", text="empty", fill=T.dim,
                          font=("Segoe UI", 12, "italic"))
        x = 522
        for i, q in enumerate(waiting):
            if x + 60 > W - 40:
                c.create_text(x, 60, anchor="w", text=f"+{len(waiting) - i}",
                              fill=T.muted, font=("Segoe UI", 11, "bold"))
                break
            col = self.col(q)
            rrect(c, x, 42, x + 54, 78, 12, fill=col, outline=lighten(col, .4))
            c.create_text(x + 27, 60, text=f"P{q}", fill=INK,
                          font=("Segoe UI", 10, "bold"))
            if i < len(waiting) - 1:
                c.create_text(x + 63, 60, text="›", fill=T.muted,
                              font=("Segoe UI", 14, "bold"))
            x += 76

    def next_start(self, pid):
        best = 10 ** 9
        for q, s, e in self.segs:
            if q == pid and s > self.t:
                best = min(best, s)
        return best

    def geom(self):
        W = max(self.gantt.winfo_width(), 700)
        total = self.segs[-1][2]
        left, right = 46, W - 38
        return W, left, right, (right - left) / total, 92, 76

    def on_gantt_move(self, e):
        if not self.segs:
            return
        W, left, right, scale, top, h = self.geom()
        hit = None
        if top <= e.y <= top + h:
            for i, (pid, s, en) in enumerate(self.segs):
                if s >= self.t:
                    break
                if left + s * scale <= e.x <= left + min(en, self.t) * scale:
                    hit = i
                    break
        self.hx, self.hy = e.x, e.y
        if hit != self.hover or hit is not None:
            self.hover = hit
            if not self.running:
                self.draw_gantt()

    def on_gantt_leave(self, e):
        if self.hover is not None:
            self.hover = None
            if not self.running:
                self.draw_gantt()

    def draw_gantt(self):
        c = self.gantt
        c.delete("all")
        W = max(c.winfo_width(), 700)
        H = int(c["height"])
        rrect(c, 2, 2, W - 2, H - 2, 18, fill=T.card, outline=T.border)
        c.create_text(26, 28, anchor="w", text="GANTT CHART", fill=T.fg,
                      font=("Segoe UI", 12, "bold"))
        rrect(c, W - 250, 14, W - 24, 42, 12, fill=T.card2, outline=T.border)
        c.create_text(W - 137, 28, text=self.status.get(), fill=T.accent2,
                      font=("Segoe UI", 10, "bold"))

        if not self.segs:
            for i in range(5):
                x0 = 46 + i * (W - 100) / 5
                rrect(c, x0, 100, x0 + (W - 130) / 5, 170, 12,
                      fill=T.idle, outline=T.idle_line, dash=(4, 4))
            c.create_text(W / 2, 135, text="Press  ▶ RUN  (F5)  or  ⏭ Step  to start",
                          fill=T.muted, font=("Segoe UI", 14, "bold"))
            self.draw_legend(c, H)
            return

        total = self.segs[-1][2]
        _, left, right, scale, top, h = self.geom()
        t = self.t
        pulse = (math.sin(time.time() * 6) + 1) / 2

        step = max(1, math.ceil(total / 20))
        for x in range(0, total + 1, step):
            gx = left + x * scale
            c.create_line(gx, top - 14, gx, top + h + 14, fill=T.grid)
        c.create_line(left, top + h + 14, right, top + h + 14, fill=T.border)

        marks = {0}
        for i, (pid, s, e) in enumerate(self.segs):
            if t <= s:
                continue
            marks.add(s)
            if t >= e:
                marks.add(e)
            ev = min(e, t)
            x0, x1 = left + s * scale, left + ev * scale
            if x1 - x0 < 1:
                continue
            running_now = s <= t < e
            hov = i == self.hover
            if pid is None:
                rrect(c, x0, top + 10, x1, top + h - 10, 12, fill=T.idle,
                      outline=T.idle_line, dash=(4, 3))
                if x1 - x0 > 40:
                    c.create_text((x0 + x1) / 2, top + h / 2, text="IDLE",
                                  fill=T.muted, font=("Segoe UI", 11, "bold"))
            else:
                col = self.col(pid)
                if running_now or hov:
                    for g, m in ((13, .88), (9, .75), (5, .55)):
                        gg = g * (0.55 + 0.45 * (pulse if running_now else 1))
                        rrect(c, x0 - gg, top - gg, x1 + gg, top + h + gg,
                              14 + gg / 2, fill=blend(col, T.card, m), outline="")
                rrect(c, x0 + 1, top + 4, x1 + 1, top + h + 4, 14,
                      fill=darken(col, .75), outline="")
                rrect(c, x0, top, x1, top + h, 14, fill=col,
                      outline=lighten(col, .45), width=1)
                if x1 - x0 > 12:
                    rrect(c, x0 + 4, top + 4, x1 - 4, top + h * .44, 10,
                          fill=lighten(col, .28), outline="")
                if x1 - x0 > 30:
                    c.create_text((x0 + x1) / 2, top + h * .5, text=f"P{pid}",
                                  fill=INK, font=("Segoe UI", 16, "bold"))
                if x1 - x0 > 58:
                    c.create_text((x0 + x1) / 2, top + h * .78, text=f"{e - s} units",
                                  fill=darken(col, .55), font=("Segoe UI", 9, "bold"))

        kept = []
        for v in sorted(marks):
            if not kept or (v - kept[-1]) * scale >= 24:
                kept.append(v)
        if total in marks and total not in kept:
            while kept and (total - kept[-1]) * scale < 24:
                kept.pop()
            kept.append(total)
        for v in kept:
            c.create_text(left + v * scale, top + h + 26, text=str(v), fill=T.fg,
                          font=("Segoe UI", 10, "bold"))

        # playhead
        px = left + min(t, total) * scale
        c.create_line(px, top - 20, px, top + h + 16, fill=blend(T.fg, T.card, .8), width=8)
        c.create_line(px, top - 20, px, top + h + 16, fill=T.fg, width=2)
        rrect(c, px - 38, top - 52, px + 38, top - 26, 10, fill=T.accent,
              outline=lighten(T.accent, .4))
        c.create_text(px, top - 39, text=f"t = {t:.1f}", fill=ink(T.accent),
                      font=("Segoe UI", 10, "bold"))
        c.create_polygon(px - 7, top - 26, px + 7, top - 26, px, top - 17,
                         fill=T.accent, outline="")

        for x, y, vx, vy, life, col in self.sparks:
            r = max(1, life / 14)
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=blend(col, T.card, 1 - min(1, life / 40)), outline="")
        self.draw_legend(c, H)

        # hover tooltip
        if self.hover is not None and self.hover < len(self.segs):
            pid, s, e = self.segs[self.hover]
            if pid is None:
                lines = ["Idle", f"{s} → {e}   ({e - s} units)"]
            else:
                lines = [f"P{pid}   {s} → {e}   ({e - s} units)"]
                d = self.info.get(pid)
                if d and d["ct"] == e:
                    lines.append(f"CT {d['ct']}  ·  TAT {d['tat']}  ·  WT {d['wt']}")
            bw = max(len(x) for x in lines) * 7 + 24
            bh = len(lines) * 18 + 14
            bx = min(self.hx + 14, W - bw - 8)
            by = max(4, self.hy - bh - 10)
            rrect(c, bx, by, bx + bw, by + bh, 10, fill=T.card2, outline=T.accent)
            for i, ln in enumerate(lines):
                c.create_text(bx + 12, by + 16 + i * 18, anchor="w", text=ln,
                              fill=T.fg, font=("Segoe UI", 9, "bold"))

    def draw_legend(self, c, H):
        x = 28
        for p in self.procs:
            col = self.col(p["pid"])
            c.create_oval(x, H - 28, x + 12, H - 16, fill=col, outline="")
            c.create_text(x + 18, H - 22, anchor="w", text=f"P{p['pid']}",
                          fill=T.muted, font=("Segoe UI", 9, "bold"))
            x += 20 + 9 * len(f"P{p['pid']}") + 14

    def draw_stats(self):
        c = self.statc
        c.delete("all")
        k = 1 - (1 - self.count) ** 3
        s = self.stats
        tiles = [
            ("AVG WAITING", T.accent, s and s["wt"] * k, "{:.2f}", "time units"),
            ("AVG TURNAROUND", T.pink, s and s["tat"] * k, "{:.2f}", "time units"),
            ("CPU UTILIZATION", T.good, s and s["util"] * k, "{:.0f}", "percent"),
            ("THROUGHPUT", T.warn, s and s["thr"] * k, "{:.3f}", "processes / unit"),
        ]
        for i, (title, col, val, fmt, unit) in enumerate(tiles):
            x0, y0 = (i % 2) * 188 + 2, (i // 2) * 90 + 2
            rrect(c, x0, y0, x0 + 178, y0 + 84, 16, fill=T.card, outline=T.border)
            rrect(c, x0, y0 + 14, x0 + 5, y0 + 70, 3, fill=col, outline="")
            c.create_text(x0 + 18, y0 + 18, anchor="w", text=title, fill=T.muted,
                          font=("Segoe UI", 8, "bold"))
            c.create_text(x0 + 18, y0 + 44, anchor="w",
                          text="—" if val is None else fmt.format(val),
                          fill=col, font=("Segoe UI", 20, "bold"))
            c.create_text(x0 + 18, y0 + 67, anchor="w", text=unit, fill=T.dim,
                          font=("Segoe UI", 8))


if __name__ == "__main__":
    App().mainloop()