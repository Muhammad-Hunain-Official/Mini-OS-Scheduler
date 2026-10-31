"""
Mini OS Scheduling Simulator  -  Neon animated UI (tkinter)
Algorithms : FCFS, SJF, Priority (non-preemptive), Round Robin (preemptive)
Run        : python gui.py      (no main.exe needed)
Shortcut   : F5 = Run
"""
import math
import random
import time
import tkinter as tk
from collections import deque
from tkinter import ttk, messagebox

MAX = 10

# ------------------------------------------------------------- palette
BG = "#0a0e1f"
CARD = "#121936"
CARD2 = "#1a2347"
BORDER = "#2b3768"
FG = "#eef1ff"
MUTED = "#8c97cc"
ACCENT = "#7c5cff"
ACCENT2 = "#22d3ee"
GOOD = "#34d399"
WARN = "#fbbf24"
BAD = "#fb7185"
PINK = "#f472b6"
COLORS = ["#ff6b81", "#ffa94d", "#ffd43b", "#69db7c", "#38d9a9",
          "#4dabf7", "#748ffc", "#b197fc", "#f783ac", "#a9e34b"]

ALGO_NAMES = {"FCFS": "FCFS", "SJF": "SJF",
              "PRIORITY": "Priority", "RR": "Round Robin"}


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


def rrect(c, x0, y0, x1, y1, r=10, **kw):
    r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return c.create_polygon(pts, smooth=True, **kw)


# ----------------------------------------------------------- scheduling
def schedule(procs, algo, quantum=2):
    """Returns (segments, info). segments: (pid|None, start, end).
    Same rules as the C program:
      SJF      -> shortest burst, tie: earlier arrival
      PRIORITY -> smaller number = higher priority, tie: earlier arrival
      RR       -> arrivals during a slice enter the queue before the
                  preempted process is put back."""
    n = len(procs)
    segs, info = [], {}
    order = sorted(procs, key=lambda p: (p["at"], p["pid"]))

    def finish(p, ct, start):
        info[p["pid"]] = {"start": start, "ct": ct,
                          "tat": ct - p["at"],
                          "wt": ct - p["at"] - p["bt"]}

    if algo != "RR":
        done, t = set(), 0
        while len(done) < n:
            avail = [p for p in order if p["pid"] not in done and p["at"] <= t]
            if not avail:
                nxt = min(p["at"] for p in order if p["pid"] not in done)
                segs.append((None, t, nxt))
                t = nxt
                continue
            if algo == "FCFS":
                p = avail[0]
            elif algo == "SJF":
                p = min(avail, key=lambda x: (x["bt"], x["at"]))
            else:  # PRIORITY
                p = min(avail, key=lambda x: (x["pr"], x["at"]))
            segs.append((p["pid"], t, t + p["bt"]))
            finish(p, t + p["bt"], t)
            t += p["bt"]
            done.add(p["pid"])
        return segs, info

    # ----- Round Robin
    rem = {p["pid"]: p["bt"] for p in procs}
    byid = {p["pid"]: p for p in procs}
    first = {}
    queue, inq = deque(), set()
    t, completed = 0, 0
    for p in order:
        if p["at"] <= t:
            queue.append(p["pid"])
            inq.add(p["pid"])
    while completed < n:
        if not queue:
            nxt = min(p["at"] for p in order if rem[p["pid"]] > 0)
            if nxt > t:
                segs.append((None, t, nxt))
            t = nxt
            for p in order:
                if rem[p["pid"]] > 0 and p["pid"] not in inq and p["at"] <= t:
                    queue.append(p["pid"])
                    inq.add(p["pid"])
        idx = queue.popleft()
        inq.discard(idx)
        run = min(quantum, rem[idx])
        first.setdefault(idx, t)
        segs.append((idx, t, t + run))
        t += run
        rem[idx] -= run
        for p in order:
            q = p["pid"]
            if q != idx and rem[q] > 0 and q not in inq and p["at"] <= t:
                queue.append(q)
                inq.add(q)
        if rem[idx] == 0:
            finish(byid[idx], t, first[idx])
            completed += 1
        else:
            queue.append(idx)
            inq.add(idx)
    return segs, info


# --------------------------------------------------------------- widgets
class RButton(tk.Canvas):
    """Rounded animated button."""

    def __init__(self, parent, text, command, color=ACCENT,
                 width=110, height=38, bg=CARD):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, cursor="hand2")
        self.w, self.h = width, height
        self.text, self.cmd, self.color = text, command, color
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
        col = lighten(self.color, 0.18) if self.hover else self.color
        if self.down:
            col = darken(self.color, 0.15)
        off = 2 if self.down else 0
        rrect(self, 1, 3, self.w - 1, self.h - 1, 12, fill=darken(col, 0.45), outline="")
        rrect(self, 1, 1 + off, self.w - 1, self.h - 3 + off, 12, fill=col, outline="")
        rrect(self, 4, 3 + off, self.w - 4, self.h * 0.45 + off, 9,
              fill=lighten(col, 0.18), outline="")
        self.create_text(self.w / 2, (self.h - 2) / 2 + off, text=self.text,
                         fill="#ffffff", font=("Segoe UI", 10, "bold"))


class Segmented(tk.Canvas):
    """Pill toggle for choosing an option."""

    def __init__(self, parent, options, variable, width=330, height=40, bg=CARD):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, cursor="hand2")
        self.options, self.var, self.w, self.h = options, variable, width, height
        self.bind("<Button-1>", self.click)
        self.var.trace_add("write", lambda *a: self.draw())
        self.draw()

    def click(self, e):
        i = min(len(self.options) - 1, int(e.x / (self.w / len(self.options))))
        self.var.set(self.options[i][1])

    def draw(self):
        self.delete("all")
        rrect(self, 1, 1, self.w - 1, self.h - 1, 18, fill=CARD2, outline=BORDER)
        seg = self.w / len(self.options)
        size = 10 if len(self.options) <= 3 else 9
        for i, (label, val) in enumerate(self.options):
            active = self.var.get() == val
            if active:
                rrect(self, i * seg + 4, 4, (i + 1) * seg - 4, self.h - 4, 15,
                      fill=ACCENT, outline=lighten(ACCENT, 0.3))
            self.create_text(i * seg + seg / 2, self.h / 2, text=label,
                             fill="#fff" if active else MUTED,
                             font=("Segoe UI", size, "bold"))


# ------------------------------------------------------------------- app
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini OS Scheduling Simulator")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1320, sw - 30), min(800, sh - 80)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 2 - 20)}")
        self.minsize(960, 560)
        self.configure(bg=BG)
        self.bind("<F5>", lambda e: self.run())

        self.procs = []
        self.segs, self.info = [], {}
        self.t = 0.0
        self.running = False
        self.after_id = None
        self.last = time.time()
        self.shown_rows = set()
        self.sparks = []
        self.stats = None
        self.count = 0.0
        self.stars = []
        self.run_algo = "FCFS"
        self.run_quantum = 2

        self.algo = tk.StringVar(value="FCFS")
        self.quantum = tk.StringVar(value="2")
        self.speed = tk.DoubleVar(value=3.0)
        self.status = tk.StringVar(value="Ready")

        self.setup_style()
        self.build_ui()
        self.algo.trace_add("write", lambda *a: self.on_algo_change())
        self.on_algo_change()
        self.load_sample()
        self.after(50, self.draw)
        self.star_loop()

    # ---------------------------------------------------------- styles
    def setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=CARD2, fieldbackground=CARD2,
                    foreground=FG, rowheight=30, borderwidth=0,
                    font=("Segoe UI", 10))
        s.configure("Treeview.Heading", background=CARD, foreground=ACCENT2,
                    font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        s.map("Treeview", background=[("selected", "#2f3b7a")])
        s.map("Treeview.Heading", background=[("active", CARD)])
        s.configure("Horizontal.TScale", background=CARD, troughcolor=CARD2)

    def card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)

    def section(self, parent, text, color=ACCENT2):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", padx=18, pady=(12, 6))
        tk.Frame(f, bg=color, width=4, height=16).pack(side="left", padx=(0, 8))
        tk.Label(f, text=text, bg=CARD, fg=FG,
                 font=("Segoe UI", 11, "bold")).pack(side="left")

    # -------------------------------------------------------------- UI
    def build_ui(self):
        self.header = tk.Canvas(self, height=88, bg=BG, highlightthickness=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self.draw_header)

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # ---------------- left control panel
        left = self.card(main)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.configure(width=390)
        left.pack_propagate(False)

        ctl = tk.Frame(left, bg=CARD)
        ctl.pack(fill="x", padx=18, pady=(14, 0))
        RButton(ctl, "▶  RUN (F5)", self.run, ACCENT, 124, 44).pack(side="left", padx=(0, 8))
        self.b_pause = RButton(ctl, "⏸ Pause", self.toggle_pause, "#0ea5e9", 104, 44)
        self.b_pause.pack(side="left", padx=(0, 8))
        RButton(ctl, "↺ Reset", self.reset, "#64748b", 104, 44).pack(side="left")

        self.section(left, "ADD PROCESS", ACCENT2)
        form = tk.Frame(left, bg=CARD)
        form.pack(fill="x", padx=18)
        self.e_at, self.e_bt, self.e_pr = tk.StringVar(), tk.StringVar(), tk.StringVar(value="1")
        self.entries = []
        for i, (lbl, var) in enumerate([("Arrival", self.e_at),
                                        ("Burst", self.e_bt),
                                        ("Priority", self.e_pr)]):
            tk.Label(form, text=lbl, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 9)).grid(row=0, column=i, sticky="w")
            e = tk.Entry(form, textvariable=var, width=7, bg=CARD2, fg=FG,
                         insertbackground=FG, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=ACCENT, font=("Segoe UI", 12),
                         justify="center")
            e.grid(row=1, column=i, padx=(0, 8), ipady=6)
            e.bind("<Return>", lambda ev: self.add_process())
            self.entries.append(e)
        RButton(form, "+ Add", self.add_process, GOOD, 80, 38).grid(row=1, column=3)

        tbl = tk.Frame(left, bg=CARD)
        tbl.pack(fill="x", padx=18, pady=8)
        cols = ("pid", "at", "bt", "pr")
        self.tree_in = ttk.Treeview(tbl, columns=cols, show="headings", height=4)
        for c, h in zip(cols, ("PID", "Arrival", "Burst", "Priority")):
            self.tree_in.heading(c, text=h)
            self.tree_in.column(c, width=72, anchor="center")
        self.tree_in.pack(fill="x")
        for i, col in enumerate(COLORS):
            self.tree_in.tag_configure(f"p{i + 1}", foreground=col)

        row = tk.Frame(left, bg=CARD)
        row.pack(fill="x", padx=18)
        RButton(row, "Remove", self.remove_process, BAD, 104, 36).pack(side="left", padx=(0, 6))
        RButton(row, "Clear", self.clear_all, "#f59e0b", 104, 36).pack(side="left", padx=(0, 6))
        RButton(row, "🎲 Random", self.load_random, "#a855f7", 104, 36).pack(side="left")

        self.section(left, "ALGORITHM", PINK)
        Segmented(left, [("FCFS", "FCFS"), ("SJF", "SJF"),
                         ("Priority", "PRIORITY"), ("R.Robin", "RR")],
                  self.algo, 352, 42).pack(padx=18)

        qrow = tk.Frame(left, bg=CARD)
        qrow.pack(fill="x", padx=18, pady=(8, 0))
        self.q_label = tk.Label(qrow, text="Time Quantum", bg=CARD, fg=MUTED,
                                font=("Segoe UI", 10, "bold"))
        self.q_label.pack(side="left")
        RButton(qrow, "+", lambda: self.step_q(1), "#334155", 34, 32).pack(side="right")
        self.q_entry = tk.Entry(qrow, textvariable=self.quantum, width=5, bg=CARD2,
                                fg=FG, insertbackground=FG, relief="flat",
                                highlightthickness=1, highlightbackground=BORDER,
                                highlightcolor=ACCENT, font=("Segoe UI", 12),
                                justify="center", disabledbackground=CARD,
                                disabledforeground="#4a5588")
        self.q_entry.pack(side="right", padx=6, ipady=3)
        RButton(qrow, "−", lambda: self.step_q(-1), "#334155", 34, 32).pack(side="right")

        self.section(left, "ANIMATION SPEED", WARN)
        sp = tk.Frame(left, bg=CARD)
        sp.pack(fill="x", padx=18)
        tk.Label(sp, text="🐢", bg=CARD, fg=FG, font=("Segoe UI", 12)).pack(side="left")
        ttk.Scale(sp, from_=1, to=20, variable=self.speed).pack(
            side="left", fill="x", expand=True, padx=8)
        tk.Label(sp, text="🐇", bg=CARD, fg=FG, font=("Segoe UI", 12)).pack(side="left")

        # ---------------- right visual area
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.hud = tk.Canvas(right, height=104, bg=BG, highlightthickness=0)
        self.hud.pack(fill="x")
        self.hud.bind("<Configure>", lambda e: self.draw())

        self.gantt = tk.Canvas(right, height=250, bg=BG, highlightthickness=0)
        self.gantt.pack(fill="x", pady=(10, 10))
        self.gantt.bind("<Configure>", lambda e: self.draw())

        bottom = tk.Frame(right, bg=BG)
        bottom.pack(fill="both", expand=True)

        rc = self.card(bottom)
        rc.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.section(rc, "RESULTS", GOOD)
        cols = ("pid", "at", "bt", "pr", "ct", "tat", "wt")
        self.tree_out = ttk.Treeview(rc, columns=cols, show="headings", height=6)
        for c, h in zip(cols, ("PID", "AT", "BT", "PR", "CT", "TAT", "WT")):
            self.tree_out.heading(c, text=h)
            self.tree_out.column(c, width=58, anchor="center")
        self.tree_out.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        for i, col in enumerate(COLORS):
            self.tree_out.tag_configure(f"p{i + 1}", foreground=col)

        self.statc = tk.Canvas(bottom, width=360, height=178, bg=BG,
                               highlightthickness=0)
        self.statc.pack(side="left", fill="y")

    # ---------------------------------------------------------- header
    def draw_header(self, e=None):
        c = self.header
        c.delete("all")
        W = max(c.winfo_width(), 800)
        for x in range(0, W, 4):
            c.create_rectangle(x, 0, x + 4, 88,
                               fill=blend("#34208f", BG, (x / W) ** 0.7), outline="")
        c.create_line(0, 87, W, 87, fill=ACCENT, width=2)
        c.create_text(32, 34, anchor="w", text="⚙  MINI OS SCHEDULING SIMULATOR",
                      fill="#1d1450", font=("Segoe UI", 21, "bold"))
        c.create_text(30, 32, anchor="w", text="⚙  MINI OS SCHEDULING SIMULATOR",
                      fill="#ffffff", font=("Segoe UI", 21, "bold"))
        c.create_text(34, 64, anchor="w",
                      text="FCFS  •  SJF  •  Priority  •  Round Robin  •  Live Gantt Chart",
                      fill=ACCENT2, font=("Segoe UI", 10, "bold"))
        self.stars = []
        for _ in range(45):
            x, y = random.randint(0, W), random.randint(4, 82)
            r = random.choice([1, 1, 2])
            item = c.create_oval(x, y, x + r * 2, y + r * 2, fill="#ffffff", outline="")
            self.stars.append([item, random.uniform(0.2, 0.9), random.random() * 6, r])

    def star_loop(self):
        c = self.header
        W = max(c.winfo_width(), 800)
        now = time.time()
        for s in self.stars:
            c.move(s[0], -s[1], 0)
            x0, _, x1, _ = c.coords(s[0])
            if x1 < 0:
                c.move(s[0], W + 10, 0)
            tw = (math.sin(now * 2 + s[2]) + 1) / 2
            c.itemconfig(s[0], fill=blend("#6a5acd", "#ffffff", tw))
        self.after(40, self.star_loop)

    # ------------------------------------------------- algorithm / quantum
    def on_algo_change(self):
        is_rr = self.algo.get() == "RR"
        self.q_entry.config(state="normal" if is_rr else "disabled")
        self.q_label.config(fg=FG if is_rr else "#4a5588")

    def step_q(self, d):
        if self.algo.get() != "RR":
            return
        try:
            q = int(self.quantum.get())
        except ValueError:
            q = 2
        self.quantum.set(str(max(1, q + d)))

    # ------------------------------------------------- process manager
    def refresh_input(self):
        self.tree_in.delete(*self.tree_in.get_children())
        for p in self.procs:
            self.tree_in.insert("", "end", tags=(f"p{p['pid']}",),
                                values=(f"P{p['pid']}", p["at"], p["bt"], p["pr"]))

    def add_process(self):
        if len(self.procs) >= MAX:
            messagebox.showwarning("Limit", f"Maximum {MAX} processes allowed.")
            return
        try:
            at, bt, pr = int(self.e_at.get()), int(self.e_bt.get()), int(self.e_pr.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Enter integers only.")
            return
        if at < 0 or bt < 1 or pr < 1:
            messagebox.showerror("Invalid input",
                                 "Arrival >= 0, Burst >= 1, Priority >= 1.")
            return
        self.procs.append({"pid": len(self.procs) + 1, "at": at, "bt": bt, "pr": pr})
        self.e_at.set("")
        self.e_bt.set("")
        self.entries[0].focus_set()
        self.refresh_input()
        self.reset()

    def remove_process(self):
        sel = self.tree_in.selection()
        if not sel:
            return
        del self.procs[self.tree_in.index(sel[0])]
        for i, p in enumerate(self.procs):
            p["pid"] = i + 1
        self.refresh_input()
        self.reset()

    def clear_all(self):
        self.procs = []
        self.refresh_input()
        self.reset()

    def load_sample(self):
        data = [(0, 6, 2), (2, 8, 1), (4, 3, 3), (20, 4, 2)]
        self.procs = [{"pid": i + 1, "at": a, "bt": b, "pr": p}
                      for i, (a, b, p) in enumerate(data)]
        self.refresh_input()

    def load_random(self):
        n = random.randint(4, 7)
        self.procs = [{"pid": i + 1, "at": random.randint(0, 10),
                       "bt": random.randint(1, 9), "pr": random.randint(1, 5)}
                      for i in range(n)]
        self.refresh_input()
        self.reset()

    # ------------------------------------------------------- animation
    def run(self):
        if not self.procs:
            messagebox.showinfo("No processes", "Add at least one process first.")
            return
        algo, q = self.algo.get(), 2
        if algo == "RR":
            try:
                q = int(self.quantum.get())
                if q < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid quantum",
                                     "Time Quantum must be an integer >= 1.")
                return
            slices = sum(-(-p["bt"] // q) for p in self.procs)
            if slices > 600:
                messagebox.showwarning("Too many slices",
                                       f"This would create {slices} time slices.\n"
                                       "Increase the Time Quantum.")
                return
        self.reset()
        self.run_algo, self.run_quantum = algo, q
        self.segs, self.info = schedule(self.procs, algo, q)
        self.t = 0.0
        self.running = True
        self.status.set(f"{ALGO_NAMES[algo]} running…")
        self.last = time.time()
        self.tick()

    def toggle_pause(self):
        if not self.segs or self.t >= self.segs[-1][2]:
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
        self.running = False
        self.segs, self.info = [], {}
        self.t, self.count, self.stats = 0.0, 0.0, None
        self.sparks = []
        self.shown_rows = set()
        self.tree_out.delete(*self.tree_out.get_children())
        self.status.set("Ready")
        self.b_pause.set_text("⏸ Pause")
        self.draw()

    def tick(self):
        if not self.running:
            return
        now = time.time()
        total = self.segs[-1][2]
        rate = self.speed.get() * max(1.0, total / 50)  # long runs stay watchable
        self.t += (now - self.last) * rate
        self.last = now
        if self.t >= total:
            self.t = float(total)
            self.running = False
            self.finish()
        self.update_rows()
        self.draw()
        if self.running:
            self.after_id = self.after(16, self.tick)

    def update_rows(self):
        for pid, d in sorted(self.info.items(), key=lambda kv: kv[1]["ct"]):
            if d["ct"] <= self.t and pid not in self.shown_rows:
                self.shown_rows.add(pid)
                p = self.procs[pid - 1]
                self.tree_out.insert("", "end", tags=(f"p{pid}",),
                                     values=(f"P{pid}", p["at"], p["bt"], p["pr"],
                                             d["ct"], d["tat"], d["wt"]))
                self.tree_out.yview_moveto(1)

    def finish(self):
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
        W = max(self.gantt.winfo_width(), 700)
        x = W - 36
        for _ in range(60):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(2, 7)
            self.sparks.append([x, 120, math.cos(ang) * sp, math.sin(ang) * sp - 2,
                                random.randint(30, 60), random.choice(COLORS)])
        self.count = 0.0
        self.after(16, self.finish_loop)

    def finish_loop(self):
        self.count = min(1.0, self.count + 0.025)
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[3] += 0.22
            s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]
        self.draw()
        if self.count < 1.0 or self.sparks:
            self.after(16, self.finish_loop)

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
        self.draw_hud()
        self.draw_gantt()
        self.draw_stats()

    def draw_hud(self):
        c = self.hud
        c.delete("all")
        W = max(c.winfo_width(), 700)
        H = 104
        kind, pid = self.current()
        total = self.segs[-1][2] if self.segs else 0
        algo = self.run_algo if self.segs else self.algo.get()

        # --- clock panel
        rrect(c, 2, 2, 230, H - 2, 18, fill=CARD, outline=BORDER)
        c.create_text(22, 24, anchor="w", text="CLOCK", fill=MUTED,
                      font=("Segoe UI", 9, "bold"))
        c.create_text(22, 54, anchor="w", text=f"{self.t:5.1f}",
                      fill=ACCENT2, font=("Consolas", 28, "bold"))
        c.create_text(150, 62, anchor="w", text="units", fill=MUTED,
                      font=("Segoe UI", 9))
        rrect(c, 22, H - 22, 210, H - 14, 4, fill=CARD2, outline="")
        if total:
            frac = self.t / total
            if frac > 0.02:
                rrect(c, 22, H - 22, 22 + 188 * frac, H - 14, 4,
                      fill=blend(ACCENT, ACCENT2, frac), outline="")

        # --- cpu panel
        rrect(c, 242, 2, 490, H - 2, 18, fill=CARD, outline=BORDER)
        c.create_text(262, 24, anchor="w", text="CPU", fill=MUTED,
                      font=("Segoe UI", 9, "bold"))
        cx, cy = 312, 62
        if kind == "run":
            col = COLORS[(pid - 1) % len(COLORS)]
            label, sub = f"P{pid}", "EXECUTING"
        elif kind == "idle":
            col, label, sub = "#64748b", "—", "IDLE"
        elif kind == "done":
            col, label, sub = GOOD, "✔", "FINISHED"
        else:
            col, label, sub = "#475569", "·", "STANDBY"
        pulse = (math.sin(time.time() * 6) + 1) / 2 if kind == "run" else 0
        for r, m in ((34, .88), (30, .78), (26, .6)):
            rr = r + pulse * 4
            c.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                          fill=blend(col, CARD, m), outline="")
        c.create_oval(cx - 22, cy - 22, cx + 22, cy + 22, fill=col,
                      outline=lighten(col, .4), width=2)
        c.create_text(cx, cy, text=label, fill="#0a0e1f",
                      font=("Segoe UI", 15, "bold"))
        c.create_text(358, 52, anchor="w", text=sub, fill=col,
                      font=("Segoe UI", 12, "bold"))
        extra = f"  ·  Q = {self.run_quantum}" if (algo == "RR" and self.segs) else ""
        c.create_text(358, 72, anchor="w", text=ALGO_NAMES[algo] + extra,
                      fill=MUTED, font=("Segoe UI", 9))

        # --- ready queue panel
        rrect(c, 502, 2, W - 2, H - 2, 18, fill=CARD, outline=BORDER)
        c.create_text(522, 24, anchor="w", text="READY QUEUE", fill=MUTED,
                      font=("Segoe UI", 9, "bold"))
        run_pid = pid if kind == "run" else None
        waiting = [p["pid"] for p in self.procs
                   if p["pid"] in self.info and p["at"] <= self.t
                   and self.info[p["pid"]]["ct"] > self.t and p["pid"] != run_pid]
        waiting.sort(key=self.next_start)
        if not waiting:
            c.create_text(522, 64, anchor="w", text="empty", fill="#46518a",
                          font=("Segoe UI", 12, "italic"))
        x = 522
        for i, q in enumerate(waiting):
            if x + 60 > W - 40:
                c.create_text(x, 64, anchor="w", text=f"+{len(waiting) - i}",
                              fill=MUTED, font=("Segoe UI", 11, "bold"))
                break
            col = COLORS[(q - 1) % len(COLORS)]
            rrect(c, x, 46, x + 50, 82, 12, fill=col, outline=lighten(col, .4))
            c.create_text(x + 25, 64, text=f"P{q}", fill="#0a0e1f",
                          font=("Segoe UI", 11, "bold"))
            if i < len(waiting) - 1:
                c.create_text(x + 58, 64, text="›", fill=MUTED,
                              font=("Segoe UI", 14, "bold"))
            x += 70

    def next_start(self, pid):
        """Start time of the next slice of this process (queue order)."""
        best = 10 ** 9
        for q, s, e in self.segs:
            if q == pid and s > self.t:
                best = min(best, s)
        return best

    def draw_gantt(self):
        c = self.gantt
        c.delete("all")
        W = max(c.winfo_width(), 700)
        H = int(c["height"])
        rrect(c, 2, 2, W - 2, H - 2, 18, fill=CARD, outline=BORDER)
        c.create_text(26, 28, anchor="w", text="GANTT CHART", fill=FG,
                      font=("Segoe UI", 12, "bold"))
        rrect(c, W - 250, 14, W - 24, 42, 12, fill=CARD2, outline=BORDER)
        c.create_text(W - 137, 28, text=self.status.get(), fill=ACCENT2,
                      font=("Segoe UI", 10, "bold"))

        if not self.segs:
            for i in range(5):
                x0 = 46 + i * (W - 100) / 5
                rrect(c, x0, 110, x0 + (W - 130) / 5, 190, 12,
                      fill="#161e40", outline="#222c5c", dash=(4, 4))
            c.create_text(W / 2, 150, text="Press  ▶ RUN  to start the simulation",
                          fill=MUTED, font=("Segoe UI", 14, "bold"))
            self.draw_legend(c, H)
            return

        total = self.segs[-1][2]
        left, right = 46, W - 38
        scale = (right - left) / total
        top, h = 92, 76
        t = self.t
        pulse = (math.sin(time.time() * 6) + 1) / 2

        # grid
        step = max(1, math.ceil(total / 20))
        for x in range(0, total + 1, step):
            gx = left + x * scale
            c.create_line(gx, top - 14, gx, top + h + 14, fill="#1c2550")
        c.create_line(left, top + h + 14, right, top + h + 14, fill=BORDER)

        marks = {0}
        for pid, s, e in self.segs:
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
            if pid is None:
                rrect(c, x0, top + 10, x1, top + h - 10, 12, fill="#151c3d",
                      outline="#47539a", dash=(4, 3))
                if x1 - x0 > 40:
                    c.create_text((x0 + x1) / 2, top + h / 2, text="IDLE",
                                  fill="#6c78b8", font=("Segoe UI", 11, "bold"))
            else:
                col = COLORS[(pid - 1) % len(COLORS)]
                if running_now:
                    for g, m in ((13, .88), (9, .75), (5, .55)):
                        gg = g * (0.55 + 0.45 * pulse)
                        rrect(c, x0 - gg, top - gg, x1 + gg, top + h + gg,
                              14 + gg / 2, fill=blend(col, CARD, m), outline="")
                rrect(c, x0 + 1, top + 4, x1 + 1, top + h + 4, 14,
                      fill=darken(col, .75), outline="")
                rrect(c, x0, top, x1, top + h, 14, fill=col,
                      outline=lighten(col, .45), width=1)
                if x1 - x0 > 12:
                    rrect(c, x0 + 4, top + 4, x1 - 4, top + h * .44, 10,
                          fill=lighten(col, .28), outline="")
                if x1 - x0 > 30:
                    c.create_text((x0 + x1) / 2, top + h * .5, text=f"P{pid}",
                                  fill="#0a0e1f", font=("Segoe UI", 16, "bold"))
                if x1 - x0 > 58:
                    c.create_text((x0 + x1) / 2, top + h * .78, text=f"{e - s} units",
                                  fill=darken(col, .55), font=("Segoe UI", 9, "bold"))

        # time labels (skip ones that would overlap)
        kept = []
        for v in sorted(marks):
            if not kept or (v - kept[-1]) * scale >= 24:
                kept.append(v)
        if total in marks and total not in kept:
            while kept and (total - kept[-1]) * scale < 24:
                kept.pop()
            kept.append(total)
        for v in kept:
            c.create_text(left + v * scale, top + h + 26, text=str(v), fill=FG,
                          font=("Segoe UI", 10, "bold"))

        # playhead
        px = left + min(t, total) * scale
        c.create_line(px, top - 20, px, top + h + 16, fill=blend("#ffffff", CARD, .75), width=8)
        c.create_line(px, top - 20, px, top + h + 16, fill="#ffffff", width=2)
        rrect(c, px - 38, top - 52, px + 38, top - 26, 10, fill=ACCENT,
              outline=lighten(ACCENT, .4))
        c.create_text(px, top - 39, text=f"t = {t:.1f}", fill="#ffffff",
                      font=("Segoe UI", 10, "bold"))
        c.create_polygon(px - 7, top - 26, px + 7, top - 26, px, top - 17,
                         fill=ACCENT, outline="")

        # sparks (celebration)
        for x, y, vx, vy, life, col in self.sparks:
            r = max(1, life / 14)
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill=blend(col, CARD, 1 - min(1, life / 40)), outline="")
        self.draw_legend(c, H)

    def draw_legend(self, c, H):
        x = 28
        for p in self.procs:
            col = COLORS[(p["pid"] - 1) % len(COLORS)]
            c.create_oval(x, H - 28, x + 12, H - 16, fill=col, outline="")
            c.create_text(x + 18, H - 22, anchor="w", text=f"P{p['pid']}",
                          fill=MUTED, font=("Segoe UI", 9, "bold"))
            x += 62

    def draw_stats(self):
        c = self.statc
        c.delete("all")
        k = 1 - (1 - self.count) ** 3
        s = self.stats
        tiles = [
            ("AVG WAITING", ACCENT, (s["wt"] * k if s else None), "{:.2f}", "units"),
            ("AVG TURNAROUND", PINK, (s["tat"] * k if s else None), "{:.2f}", "units"),
            ("CPU UTILIZATION", GOOD, (s["util"] * k if s else None), "{:.0f}", "%"),
            ("THROUGHPUT", WARN, (s["thr"] * k if s else None), "{:.3f}", "proc/unit"),
        ]
        for i, (title, col, val, fmt, unit) in enumerate(tiles):
            x0 = (i % 2) * 182 + 2
            y0 = (i // 2) * 90 + 2
            rrect(c, x0, y0, x0 + 172, y0 + 84, 16, fill=CARD, outline=BORDER)
            rrect(c, x0, y0 + 14, x0 + 5, y0 + 70, 3, fill=col, outline="")
            c.create_text(x0 + 18, y0 + 18, anchor="w", text=title, fill=MUTED,
                          font=("Segoe UI", 8, "bold"))
            c.create_text(x0 + 18, y0 + 44, anchor="w",
                          text="—" if val is None else fmt.format(val),
                          fill=col, font=("Segoe UI", 20, "bold"))
            c.create_text(x0 + 18, y0 + 67, anchor="w", text=unit, fill="#5d69a8",
                          font=("Segoe UI", 8))


if __name__ == "__main__":
    App().mainloop()