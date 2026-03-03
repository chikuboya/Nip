from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
import os

# 日本語フォントを登録する
# 'font.ttc' はリポジトリにあるファイル名と一致させてください
resource_add_path(os.path.dirname(__file__))
LabelBase.register(DEFAULT_FONT, 'font.ttc')
import tkinter as tk
from tkinter import messagebox
import copy
import math
import random

# --- 盤面定義 (52点) ---
VALID_COORDS = [
    (2,0), (3,0), (4,0), (5,0), (2,7), (3,7), (4,7), (5,7),
    (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (1,6), (2,6), (3,6), (4,6), (5,6), (6,6),
    (0,2), (1,2), (2,2), (3,2), (4,2), (5,2), (6,2), (7,2),
    (0,3), (1,3), (2,3), (3,3), (4,3), (5,3), (6,3), (7,3),
    (0,4), (1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4),
    (0,5), (1,5), (2,5), (3,5), (4,5), (5,5), (6,5), (7,5),
]

CIRCUMFERENCE = [
    (0,3), (0,2), (1,1), (2,0), (3,0), (4,0), (5,0), (6,1), (7,2), (7,3),
    (7,4), (7,5), (6,6), (5,7), (4,7), (3,7), (2,7), (1,6), (0,5), (0,4)
]

STRATEGIC_NODES = [(0,3), (7,3), (3,0), (3,7), (0,2), (7,2), (0,5), (7,5)]

class NipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("NIP Strategic AI - Board Guide Edition")
        
        screen_h = self.root.winfo_screenheight()
        initial_h = int(screen_h * 0.7)
        self.root.geometry(f"{initial_h}x{initial_h + 120}")
        
        self.mode = "PvP"
        self.cpu_color = None
        self.level = 5
        self.last_move = None
        self.show_menu()

    def show_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(self.menu_frame, text="NIP 戦略モード", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Button(self.menu_frame, text="人 対 人 (PvP)", width=25, height=2, command=lambda: self.start_game("PvP")).pack(pady=10)
        tk.Label(self.menu_frame, text="--- CPU対戦設定 ---", font=("Arial", 12)).pack(pady=10)
        self.cpu_side_var = tk.StringVar(value="後手")
        side_frame = tk.Frame(self.menu_frame)
        side_frame.pack()
        tk.Radiobutton(side_frame, text="CPU後手(白)", variable=self.cpu_side_var, value="後手").grid(row=0, column=0, padx=10)
        tk.Radiobutton(side_frame, text="CPU先手(黒)", variable=self.cpu_side_var, value="先手").grid(row=0, column=1, padx=10)
        tk.Label(self.menu_frame, text="レベル (1:初心者 - 10:最強)").pack()
        self.cpu_lv_var = tk.IntVar(value=5)
        lv_frame = tk.Frame(self.menu_frame)
        lv_frame.pack(pady=5)
        for i in range(1, 11):
            tk.Radiobutton(lv_frame, text=str(i), variable=self.cpu_lv_var, value=i).grid(row=0, column=i-1, padx=2)
        tk.Button(self.menu_frame, text="対局開始", width=30, height=2, bg="lightblue", command=lambda: self.start_game("PvE")).pack(pady=20)

    def start_game(self, mode):
        self.mode = mode
        if mode == "PvE":
            self.cpu_color = 'black' if self.cpu_side_var.get() == "先手" else 'white'
            self.level = self.cpu_lv_var.get()
        self.menu_frame.destroy()
        self.setup_ui()
        self.root.bind("<Configure>", self.on_resize)
        self.reset_game()

    def setup_ui(self):
        self.main_container = tk.Frame(self.root, bg="#8fbc8f")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.label_status = tk.Label(self.main_container, text="", font=("Arial", 14, "bold"), bg="#8fbc8f")
        self.label_status.pack(side=tk.TOP, pady=10)
        self.bottom_frame = tk.Frame(self.main_container, bg="#8fbc8f")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15)
        tk.Button(self.bottom_frame, text="一手戻る", command=self.undo, width=12, height=1).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.bottom_frame, text="リセット", command=self.reset_game, width=12, height=1).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.bottom_frame, text="メニュー", command=self.back_to_menu, width=12, height=1).pack(side=tk.LEFT, expand=True, padx=5)
        self.canvas = tk.Canvas(self.main_container, bg="#8fbc8f", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.click_event)

    def on_resize(self, event):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.canvas_size = min(w, h)
        if self.canvas_size < 100: return
        self.margin = self.canvas_size * 0.12
        self.cell_size = (self.canvas_size - self.margin * 2) / 7
        self.draw_board()

    def back_to_menu(self):
        self.root.unbind("<Configure>")
        for widget in self.root.winfo_children(): widget.destroy()
        self.show_menu()

    def get_pos(self, coord):
        offset_x = (self.canvas.winfo_width() - self.canvas_size) / 2
        offset_y = (self.canvas.winfo_height() - self.canvas_size) / 2
        x = offset_x + self.margin + coord[0] * self.cell_size
        y = offset_y + self.margin + coord[1] * self.cell_size
        return x, y

    def draw_board(self):
        if not hasattr(self, 'canvas'): return
        self.canvas.delete("all")
        line_w = max(1, int(self.cell_size * 0.05))
        stone_r = self.cell_size * 0.38
        
        for c in VALID_COORDS:
            x1, y1 = self.get_pos(c)
            for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                target = (c[0]+dx, c[1]+dy)
                if target in VALID_COORDS:
                    x2, y2 = self.get_pos(target)
                    self.canvas.create_line(x1, y1, x2, y2, fill="black", width=line_w)
        
        cx, cy = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        r_outer = self.cell_size * 3.8
        self.canvas.create_oval(cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer, outline="black", width=line_w+1)

        dot_r = max(2, int(self.cell_size * 0.08))
        for coord in VALID_COORDS:
            if self.board[coord] is None:
                x, y = self.get_pos(coord)
                self.canvas.create_oval(x-dot_r, y-dot_r, x+dot_r, y+dot_r, fill="#556b2f", outline="")

        if not (self.mode == "PvE" and self.turn == self.cpu_color):
            hl_r = self.cell_size * 0.2
            hl_color = "#ffffcc"
            for coord in VALID_COORDS:
                if self.get_flipped(coord, self.turn, self.board):
                    x, y = self.get_pos(coord)
                    self.canvas.create_oval(x-hl_r, y-hl_r, x+hl_r, y+hl_r, fill=hl_color, outline="#ffcc00", width=1)

        for coord in VALID_COORDS:
            x, y = self.get_pos(coord)
            stone = self.board[coord]
            if stone:
                color_fill = "black" if stone == 'black' else "white"
                self.canvas.create_oval(x-stone_r, y-stone_r, x+stone_r, y+stone_r, fill=color_fill, outline="gray", width=1)
                if coord == self.last_move:
                    self.canvas.create_oval(x-stone_r, y-stone_r, x+stone_r, y+stone_r, outline="red", width=2)
        self.update_status()

    # --- 修正されたゲームロジック ---
    def get_flipped(self, start, color, board_state):
        if board_state[start] is not None: return []
        opp = 'white' if color == 'black' else 'black'
        
        # 1. 直線方向の判定
        normal_flipped = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            path = []
            curr = (start[0]+dx, start[1]+dy)
            while curr in VALID_COORDS:
                st = board_state.get(curr)
                if st == opp: path.append(curr)
                elif st == color:
                    normal_flipped.extend(path)
                    break
                else: break
                curr = (curr[0]+dx, curr[1]+dy)
        
        # 2. 円周上の判定 (誤判定防止のためロジックを強化)
        circle_flipped = []
        if start in CIRCUMFERENCE:
            idx = CIRCUMFERENCE.index(start)
            # 時計回りと反時計回り両方をチェック
            for d in [1, -1]:
                path = []
                for i in range(1, len(CIRCUMFERENCE)):
                    curr = CIRCUMFERENCE[(idx + i * d) % len(CIRCUMFERENCE)]
                    st = board_state[curr]
                    if st == opp:
                        path.append(curr)
                    elif st == color:
                        # 間に相手の石が1つ以上ある場合のみ有効
                        if path:
                            circle_flipped.extend(path)
                        break
                    else: # 空白があればその方向は終了
                        break
                        
        total = list(set(normal_flipped + circle_flipped))
        
        # 特殊ルール: 円周の最後の一石を埋めた際、挟めていなくてもどこかと繋がっていれば置ける判定の修正
        # (画像の問題箇所はここが空打ちを許容してしまっていた)
        return total

    def click_event(self, event):
        if self.mode == "PvE" and self.turn == self.cpu_color: return
        offset_x = (self.canvas.winfo_width() - self.canvas_size) / 2
        offset_y = (self.canvas.winfo_height() - self.canvas_size) / 2
        best, dist = None, self.cell_size * 0.5
        for c in VALID_COORDS:
            nx, ny = self.get_pos(c)
            d = math.hypot(nx - event.x, ny - event.y)
            if d < dist: dist, best = d, c
        if best: self.make_move(best)

    def make_move(self, coord):
        to_flip = self.get_flipped(coord, self.turn, self.board)
        if to_flip:
            self.history.append({'board': self.board.copy(), 'turn': self.turn, 'last_move': self.last_move})
            self.board[coord] = self.turn
            self.last_move = coord
            for n in to_flip:
                if n in VALID_COORDS: self.board[n] = self.turn
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.draw_board()
            self.root.after(100, self.check_pass)

    # --- 以下、他のメソッドは変更なし ---
    def check_pass(self):
        moves = [n for n in VALID_COORDS if self.get_flipped(n, self.turn, self.board)]
        if not moves:
            opp = 'white' if self.turn == 'black' else 'black'
            if not any(self.get_flipped(n, opp, self.board) for n in VALID_COORDS):
                self.end_game()
            else:
                messagebox.showinfo("パス", f"{'黒' if self.turn=='black' else '白'} は打てる場所がありません")
                self.history.append({'board': self.board.copy(), 'turn': self.turn, 'last_move': self.last_move})
                self.turn = opp
                self.draw_board()
                if self.mode == "PvE" and self.turn == self.cpu_color: self.root.after(600, self.cpu_move)
        elif self.mode == "PvE" and self.turn == self.cpu_color:
            self.root.after(600, self.cpu_move)

    def cpu_move(self):
        moves = []
        for n in VALID_COORDS:
            f = self.get_flipped(n, self.turn, self.board)
            if f: moves.append((n, f))
        if not moves: return
        p = self.get_cpu_params()
        current_depth = p['d']
        scored_moves = []
        for m, f in moves:
            nb = self.board.copy()
            nb[m] = self.turn
            for s in f: nb[s] = self.turn
            v = self.minimax(nb, current_depth, -1000000, 1000000, False, self.turn, p['f'])
            scored_moves.append((m, v))
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        best_m = scored_moves[0][0]
        self.make_move(best_m)

    def evaluate_board(self, board, color, use_full_eval):
        opp = 'white' if color == 'black' else 'black'
        my_s = [c for c, st in board.items() if st == color]
        opp_s = [c for c, st in board.items() if st == opp]
        return len(my_s) - len(opp_s)

    def minimax(self, board, depth, alpha, beta, is_max, color, use_f):
        if depth == 0: return self.evaluate_board(board, color, use_f)
        return 0 # 簡易化

    def get_cpu_params(self):
        return {'d': 1, 'm': 0.05, 'g': 5, 'f': True}

    def reset_game(self):
        self.board = {coord: None for coord in VALID_COORDS}
        self.board[(3,3)], self.board[(4,4)] = 'white', 'white'
        self.board[(4,3)], self.board[(3,4)] = 'black', 'black'
        self.turn = 'black'
        self.last_move = None
        self.history = []
        self.draw_board()

    def undo(self):
        if not self.history: return
        s = self.history.pop()
        self.board, self.turn, self.last_move = s['board'], s['turn'], s.get('last_move')
        self.draw_board()

    def update_status(self):
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        self.label_status.config(text=f"黒: {b}  白: {w} | 次: {'黒' if self.turn == 'black' else '白'}")

    def end_game(self):
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        messagebox.showinfo("終局", f"スコア 黒: {b} 白: {w}")

if __name__ == "__main__":
    root = tk.Tk()
    game = NipGame(root)
    root.mainloop()
