"""GUI版BINGO抽選機。"""

import random as rd
import threading
import tkinter as tk


BINGO_MAX = 75
SPIN_STEPS = 18
BACKGROUND = "#0D1424"
PANEL = "#151F32"
TEXT = "#F4F7FB"
MUTED = "#9AA8BC"
GOLD = "#F4C45E"

COLUMNS = (
    ("B", 1, 15, "#2496E8"),
    ("I", 16, 30, "#9A70F5"),
    ("N", 31, 45, "#21B887"),
    ("G", 46, 60, "#F3A83B"),
    ("O", 61, 75, "#F06B79"),
)


class App(tk.Tk):
    """抽選演出と番号履歴を表示するBINGOアプリ。"""

    def __init__(self):
        """ウィンドウと抽選状態を初期化する。"""
        super().__init__()
        self.title("BINGO 抽選機")
        self.configure(bg=BACKGROUND)
        self.geometry("1440x900")
        self.minsize(1120, 760)

        self.remaining = list(range(1, BINGO_MAX + 1))
        self.drawn = set()
        self.cells = {}
        self.preview_num = None
        self.is_spinning = False

        self.create_widgets()

    def create_widgets(self):
        """ヘッダー、抽選パネル、番号一覧を配置する。"""
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = tk.Frame(self, bg=BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(22, 12))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header, text="BINGO", bg=BACKGROUND, fg=TEXT,
            font=("Segoe UI", 28, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.count_label = tk.Label(
            header, text="抽選済み  0 / 75", bg=PANEL, fg=TEXT,
            font=("Segoe UI", 13, "bold"), padx=18, pady=10,
        )
        self.count_label.grid(row=0, column=1, rowspan=2, sticky="e")

        body = tk.Frame(self, bg=BACKGROUND)
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        body.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        self.create_draw_panel(body)
        self.create_board(body)

    def create_draw_panel(self, parent):
        """抽選ボールと抽選ボタンを含むパネルを作成する。"""
        panel = tk.Frame(parent, bg=PANEL, padx=24, pady=24)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        self.ball_canvas = tk.Canvas(
            panel, width=310, height=310, bg=PANEL, highlightthickness=0,
        )
        self.ball_canvas.grid(row=1, column=0)
        self.show_ball(None, None)

        self.button = tk.Button(
            panel, text="START", command=self.button_event,
            font=("Segoe UI", 18, "bold"), bg=GOLD, fg="#172033",
            activebackground="#FFDA7C", activeforeground="#172033",
            disabledforeground="#667085", relief="flat", bd=0,
            cursor="hand2", padx=24, pady=14,
        )
        self.button.grid(row=4, column=0, sticky="ew")

    def create_board(self, parent):
        """B・I・N・G・Oの各15番号を並べた履歴一覧を作成する。"""
        board = tk.Frame(parent, bg=PANEL, padx=20, pady=18)
        board.grid(row=0, column=1, sticky="nsew")
        for col in range(5):
            board.columnconfigure(col, weight=1, uniform="bingo-columns")
        for row in range(3, 18):
            board.rowconfigure(row, weight=1, uniform="bingo-rows")

        for col, (letter, start, end, color) in enumerate(COLUMNS):
            heading = tk.Frame(board, bg=color, padx=6, pady=7)
            heading.grid(row=2, column=col, sticky="ew", padx=4, pady=(0, 7))
            heading.columnconfigure(0, weight=1)
            tk.Label(
                heading, text=letter, bg=color, fg="white",
                font=("Segoe UI", 17, "bold"),
            ).grid(row=0, column=0)
            tk.Label(
                heading, text=f"{start}–{end}", bg=color, fg="white",
                font=("Segoe UI", 9, "bold"),
            ).grid(row=1, column=0)

            for offset in range(15):
                num = start + offset
                cell = tk.Label(
                    board, text=f"{num:02d}", bg="#465366", fg="#F3F6FA",
                    font=("Segoe UI", 14, "bold"), height=1,
                    padx=4, pady=3,
                )
                cell.grid(row=3 + offset, column=col, sticky="ew", padx=4, pady=2)
                self.cells[num] = cell

    def button_event(self):
        """ボタン操作を受け取り、抽選演出を開始する。"""
        if self.is_spinning or not self.remaining:
            return
        self.is_spinning = True
        self.button.configure(state="disabled", text="抽選中…", cursor="arrow")
        self.spin_tick(0)

    def spin_tick(self, step):
        """候補番号と効果音を更新し、演出の次の段階を予約する。"""
        if not self.remaining:
            self.finish_draw()
            return

        candidate = rd.choice(self.remaining)
        self.set_preview(candidate)
        self.show_ball(candidate, rolling=True)
        self.play_tones(((650 + min(step, SPIN_STEPS) * 45, 28),))

        if step < SPIN_STEPS:
            # Tick間隔を少しずつ延ばし、最後に向けて減速する演出にする。
            self.after(45 + step * 9, lambda: self.spin_tick(step + 1))
        else:
            self.after(230, self.finish_draw)

    def finish_draw(self):
        """番号を1つ確定し、履歴・表示・ボタン状態を更新する。"""
        try:
            num = self.remaining.pop(rd.randrange(len(self.remaining)))
            self.drawn.add(num)
            self.set_preview(None)
            self.set_cell_drawn(num)
            self.show_ball(num)
            self.play_tones(((880, 90), (1175, 100), (1568, 210)))
            self.count_label.configure(text=f"抽選済み  {len(self.drawn)} / {BINGO_MAX}")
            self.update_button_state()
        except Exception as exc:
            print(exc)
            self.set_preview(None)
            self.show_ball(None, None)
            self.button.configure(state="normal", text="NEXT", cursor="hand2")
        finally:
            self.is_spinning = False

    def play_tones(self, notes):
        """指定した音程と長さの効果音を非同期で再生する。"""
        try:
            import winsound
        except ImportError:
            self.bell()
            return

        def play():
            try:
                for frequency, duration in notes:
                    winsound.Beep(frequency, duration)
            except (OSError, RuntimeError):
                pass

        threading.Thread(target=play, daemon=True).start()

    def set_preview(self, num):
        """抽選候補の強調表示を切り替える。"""
        if self.preview_num is not None and self.preview_num not in self.drawn:
            self.style_cell(self.preview_num, "base")
        self.preview_num = num
        if num is not None and num not in self.drawn:
            self.style_cell(num, "preview")

    def set_cell_drawn(self, num):
        """確定番号のセルを当選済みの表示にする。"""
        self.style_cell(num, "drawn")

    def style_cell(self, num, state):
        """番号セルを未抽選・候補・当選済みの配色にする。"""
        cell = self.cells[num]
        if state == "drawn":
            cell.configure(bg="#176B48", fg="#FFFFFF")
        elif state == "preview":
            cell.configure(bg="#FFE4A3", fg="#6C4A00")
        else:
            cell.configure(bg="#465366", fg="#F3F6FA")

    def show_ball(self, num, rolling=False):
        """番号と抽選状態に合わせてボールの表示を描き直す。"""
        canvas = self.ball_canvas
        canvas.delete("all")
        if num is None:
            ring_color = "#465366"
        elif rolling:
            ring_color = GOLD
        else:
            ring_color = "#21B887"
        canvas.create_oval(10, 10, 300, 300, fill="#10192A", outline="#33435D", width=2)
        canvas.create_oval(24, 24, 286, 286, fill="#F4F7FB", outline=ring_color, width=7)
        canvas.create_text(
            155, 75, text="BINGO BALL", fill="#65738A",
            font=("Segoe UI", 11, "bold"),
        )

        if num is None:
            canvas.create_text(155, 146, text="READY", fill="#516078", font=("Segoe UI", 22, "bold"))
            canvas.create_text(155, 210, text="—", fill="#26334A", font=("Segoe UI", 64, "bold"))
            return

        letter, _, _, color = COLUMNS[(num - 1) // 15]
        canvas.create_text(155, 126, text=letter, fill=color, font=("Segoe UI", 26, "bold"))
        canvas.create_text(155, 204, text=str(num), fill="#172033", font=("Segoe UI", 68, "bold"))
        if rolling:
            canvas.create_text(155, 250, text="抽選中", fill="#7D899B", font=("Segoe UI", 10, "bold"))

    def update_button_state(self):
        """残り番号の有無に応じてボタン表示と操作可否を更新する。"""
        if not self.remaining:
            self.button.configure(state="disabled", text="終了", cursor="arrow")
        else:
            self.button.configure(state="normal", text="NEXT", cursor="hand2")


def main():
    """GUIを起動し、Tkのイベントループを実行する。"""
    App().mainloop()


if __name__ == "__main__":
    main()
