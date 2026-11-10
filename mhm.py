import random
import tkinter as tk

# ---------- Стиль ----------
BG, PANEL, PANEL2 = "#0a0e1a", "#131a2e", "#1f2a4a"
TEXT, MUTED = "#e8ecf6", "#7f8bab"
GREEN, CYAN, PINK, RED, GOLD = "#4ade80", "#22d3ee", "#e879f9", "#fb7185", "#fbbf24"
FONT = "Segoe UI"
ATTEMPTS = 10
W = 556  # ширина рабочей области

# (название, максимум, цвет, описание, множитель очков)
MODES = [
    ("ЛЁГКИЙ", 10, GREEN, "Разминка", 1),
    ("НОРМАЛЬНЫЙ", 50, CYAN, "Для уверенных", 2),
    ("СЛОЖНЫЙ", 100, PINK, "Нужна стратегия", 3),
    ("ХАРДКОР", 1000, RED, "Только деление пополам", 5),
]


def lighten(hex_color, k=0.25):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * k) for c in (r, g, b))


def make_button(parent, text, color, command, size=14, pad=(26, 12)):
    b = tk.Label(parent, text=text, bg=color, fg=BG, cursor="hand2",
                 font=(FONT, size, "bold"), padx=pad[0], pady=pad[1])
    b.bind("<Button-1>", lambda e: command())
    b.bind("<Enter>", lambda e: b.config(bg=lighten(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Угадай число")
        self.geometry("620x780")
        self.minsize(600, 740)
        self.configure(bg=BG)
        self.wins = self.losses = 0
        self.best = {}
        self.screen = None
        self.show_menu()

    def switch(self):
        if self.screen is not None:
            self.screen.destroy()
        self.screen = tk.Frame(self, bg=BG)
        self.screen.pack(fill="both", expand=True, padx=32, pady=28)
        return self.screen

    # ---------- Меню ----------
    def show_menu(self):
        f = self.switch()
        tk.Label(f, text="УГАДАЙ ЧИСЛО", bg=BG, fg=TEXT,
                 font=(FONT, 34, "bold")).pack(pady=(18, 4))
        tk.Label(f, text="У тебя %d попыток. Выбери режим." % ATTEMPTS, bg=BG,
                 fg=MUTED, font=(FONT, 13)).pack(pady=(0, 20))
        for mode in MODES:
            self.mode_card(f, mode)
        tk.Label(f, text="Победы: %d     Поражения: %d" % (self.wins, self.losses),
                 bg=BG, fg=MUTED, font=(FONT, 12)).pack(side="bottom", pady=(10, 0))

    def mode_card(self, parent, mode):
        name, top, color, desc, _ = mode
        card = tk.Frame(parent, bg=PANEL, cursor="hand2")
        card.pack(fill="x", pady=7)
        tk.Frame(card, bg=color, width=6).pack(side="left", fill="y")
        body = tk.Frame(card, bg=PANEL)
        body.pack(side="left", fill="both", expand=True, padx=16, pady=14)
        if name in self.best:
            desc += "  |  рекорд %d" % self.best[name]
        n = tk.Label(body, text=name, bg=PANEL, fg=color, anchor="w",
                     font=(FONT, 16, "bold"))
        n.pack(fill="x")
        d = tk.Label(body, text=desc, bg=PANEL, fg=MUTED, anchor="w",
                     font=(FONT, 11))
        d.pack(fill="x")
        r = tk.Label(card, text="1 – %d" % top, bg=PANEL, fg=TEXT,
                     font=(FONT, 18, "bold"))
        r.pack(side="right", padx=18)
        parts = (card, body, n, d, r)

        def paint(c):
            for w in parts:
                w.config(bg=c)

        for w in parts:
            w.bind("<Enter>", lambda e: paint(PANEL2))
            w.bind("<Leave>", lambda e: paint(PANEL))
            w.bind("<Button-1>", lambda e: self.start(mode))

    # ---------- Игра ----------
    def start(self, mode):
        self.mode = mode
        top = mode[1]
        self.number = random.randint(1, top)
        self.left = ATTEMPTS
        self.low, self.high = 1, top
        self.history = []
        self.over = False
        self.build_play()

    def build_play(self):
        name, top, color, _, _ = self.mode
        f = self.switch()
        bar = tk.Frame(f, bg=BG)
        bar.pack(fill="x")
        back = tk.Label(bar, text="← Режимы", bg=BG, fg=MUTED,
                        font=(FONT, 12), cursor="hand2")
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self.show_menu())
        tk.Label(bar, text=name, bg=BG, fg=color,
                 font=(FONT, 14, "bold")).pack(side="right")

        tk.Label(f, text="Число от 1 до %d" % top, bg=BG, fg=TEXT,
                 font=(FONT, 26, "bold")).pack(pady=(24, 2))
        self.msg = tk.Label(f, text="Сделай первую попытку", bg=BG, fg=MUTED,
                            font=(FONT, 15))
        self.msg.pack(pady=(0, 16))

        self.range_c = tk.Canvas(f, width=W, height=70, bg=BG, highlightthickness=0)
        self.range_c.pack()
        self.lives_c = tk.Canvas(f, width=W, height=36, bg=BG, highlightthickness=0)
        self.lives_c.pack(pady=(8, 0))
        self.left_lbl = tk.Label(f, bg=BG, fg=MUTED, font=(FONT, 12))
        self.left_lbl.pack()

        self.box = tk.Frame(f, bg=BG)
        self.box.pack(fill="x", padx=30, pady=(20, 0))
        self.entry = tk.Entry(self.box, bg=PANEL, fg=TEXT, insertbackground=color,
                              font=(FONT, 30, "bold"), justify="center", relief="flat",
                              highlightthickness=2, highlightbackground=PANEL2,
                              highlightcolor=color, disabledbackground=PANEL,
                              disabledforeground=MUTED)
        self.entry.pack(fill="x", ipady=10)
        self.entry.bind("<Return>", lambda e: self.guess())
        make_button(self.box, "УГАДАТЬ", color, self.guess, 15, (0, 12)).pack(
            fill="x", pady=(12, 0))

        self.hist = tk.Frame(f, bg=BG)
        self.hist.pack(pady=(20, 0))
        self.refresh()
        self.entry.focus_set()

    def guess(self):
        if self.over:
            return
        top, color = self.mode[1], self.mode[2]
        try:
            g = int(self.entry.get().strip())
        except ValueError:
            return self.say("Введи целое число", RED, True)
        if not 1 <= g <= top:
            return self.say("Число должно быть от 1 до %d" % top, RED, True)
        if any(g == h for h, _ in self.history):
            return self.say("Это число уже было", GOLD, True)

        self.entry.delete(0, "end")
        self.left -= 1
        if g == self.number:
            self.history.append((g, "="))
            return self.end(True)

        dist = abs(g - self.number) / top
        heat = "Горячо" if dist <= 0.05 else "Тепло" if dist <= 0.15 else "Холодно"
        if g < self.number:
            self.low = max(self.low, g + 1)
            self.history.append((g, "↑"))
            self.say("Больше ↑   •   %s" % heat, CYAN, True)
        else:
            self.high = min(self.high, g - 1)
            self.history.append((g, "↓"))
            self.say("Меньше ↓   •   %s" % heat, PINK, True)
        self.refresh()
        if self.left == 0:
            self.end(False)

    def say(self, text, col, shake=False):
        self.msg.config(text=text, fg=col)
        if shake:
            self.shake()

    def shake(self, i=0):
        offs = [10, -10, 8, -8, 4, -4, 0]
        if i < len(offs):
            try:
                self.box.pack_configure(padx=(30 + offs[i], 30 - offs[i]))
                self.after(25, lambda: self.shake(i + 1))
            except tk.TclError:
                pass

    def refresh(self):
        top, color = self.mode[1], self.mode[2]
        # диапазон
        c = self.range_c
        c.delete("all")
        pad, y = 24, 48
        span = W - 2 * pad
        px = lambda v: pad + (v - 1) / (top - 1) * span
        c.create_line(pad, y, W - pad, y, fill=PANEL2, width=10, capstyle="round")
        c.create_line(px(self.low), y, px(self.high), y, fill=color, width=10,
                      capstyle="round")
        for v in (self.low, self.high):
            c.create_oval(px(v) - 9, y - 9, px(v) + 9, y + 9, fill=TEXT,
                          outline=color, width=3)
        c.create_text(pad, 16, text="1", fill=MUTED, anchor="w", font=(FONT, 11))
        c.create_text(W - pad, 16, text=str(top), fill=MUTED, anchor="e",
                      font=(FONT, 11))
        c.create_text(W / 2, 16, text="Сейчас: %d – %d" % (self.low, self.high),
                      fill=TEXT, font=(FONT, 12, "bold"))
        # попытки
        c = self.lives_c
        c.delete("all")
        x0 = (W - ATTEMPTS * 54) / 2 + 27
        for i in range(ATTEMPTS):
            on = i < self.left
            c.create_oval(x0 + i * 54 - 14, 4, x0 + i * 54 + 14, 32,
                          fill=color if on else PANEL,
                          outline=color if on else PANEL2, width=2)
        self.left_lbl.config(text="Осталось попыток: %d" % self.left)
        # история
        for w in self.hist.winfo_children():
            w.destroy()
        for i, (g, res) in enumerate(self.history):
            col = {"↑": CYAN, "↓": PINK, "=": GREEN}[res]
            tk.Label(self.hist, text="%d %s" % (g, res), bg=PANEL, fg=col, width=8,
                     pady=6, font=(FONT, 12, "bold")).grid(
                row=i // 5, column=i % 5, padx=4, pady=4)

    # ---------- Конец игры ----------
    def end(self, won):
        self.over = True
        name, top, color, _, mult = self.mode
        self.entry.config(state="disabled")
        self.refresh()
        if won:
            self.wins += 1
            score = (self.left + 1) * 100 * mult
            self.best[name] = max(self.best.get(name, 0), score)
            head, hc = "ПОБЕДА", GREEN
            line = "Число %d угадано за %d из %d" % (
                self.number, ATTEMPTS - self.left, ATTEMPTS)
            extra = "Очки: %d     Рекорд: %d" % (score, self.best[name])
        else:
            self.losses += 1
            head, hc = "ПОРАЖЕНИЕ", RED
            line = "Загадано было число %d" % self.number
            extra = "Попытки закончились"

        card = tk.Frame(self.screen, bg=PANEL, highlightthickness=2,
                        highlightbackground=hc)
        card.place(relx=0.5, rely=0.5, anchor="center")
        inner = tk.Frame(card, bg=PANEL)
        inner.pack(padx=44, pady=32)
        title = tk.Label(inner, text=head, bg=PANEL, fg=hc, font=(FONT, 34, "bold"))
        title.pack()
        tk.Label(inner, text=line, bg=PANEL, fg=TEXT, font=(FONT, 14)).pack(pady=(10, 2))
        tk.Label(inner, text=extra, bg=PANEL, fg=MUTED, font=(FONT, 12)).pack(
            pady=(0, 22))
        make_button(inner, "ИГРАТЬ СНОВА", color, lambda: self.start(self.mode)).pack(
            fill="x")
        make_button(inner, "РЕЖИМЫ", PANEL2, self.show_menu).pack(fill="x", pady=(10, 0))
        if won:
            self.flash(title, [GREEN, CYAN, PINK, GOLD] * 3)

    def flash(self, label, colors, i=0):
        if i < len(colors):
            try:
                label.config(fg=colors[i])
                self.after(120, lambda: self.flash(label, colors, i + 1))
            except tk.TclError:
                pass


if __name__ == "__main__":
    App().mainloop()
