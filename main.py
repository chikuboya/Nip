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
        self.last_move = None  # 最後に置いた石を記録
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
        
        # 1. 盤面の線を描画
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

        # 2. 有効な全交点にガイドドットを描画
        dot_r = max(2, int(self.cell_size * 0.08))
        for coord in VALID_COORDS:
            if self.board[coord] is None:
                x, y = self.get_pos(coord)
                self.canvas.create_oval(x-dot_r, y-dot_r, x+dot_r, y+dot_r, fill="#556b2f", outline="")

        # 3. 置ける場所のハイライト (手番プレイヤー用)
        if not (self.mode == "PvE" and self.turn == self.cpu_color):
            hl_r = self.cell_size * 0.2
            hl_color = "#ffffcc"
            for coord in VALID_COORDS:
                if self.get_flipped(coord, self.turn, self.board):
                    x, y = self.get_pos(coord)
                    self.canvas.create_oval(x-hl_r, y-hl_r, x+hl_r, y+hl_r, fill=hl_color, outline="#ffcc00", width=1)

        # 4. 石の描画
        for coord in VALID_COORDS:
            x, y = self.get_pos(coord)
            stone = self.board[coord]
            if stone:
                color_fill = "black" if stone == 'black' else "white"
                self.canvas.create_oval(x-stone_r, y-stone_r, x+stone_r, y+stone_r, fill=color_fill, outline="gray", width=1)
                
                # 最後に置いた石を強調（赤いリング）
                if coord == self.last_move:
                    self.canvas.create_oval(x-stone_r, y-stone_r, x+stone_r, y+stone_r, outline="red", width=2)
        
        self.update_status()

    # --- CPU 思考エンジン (変更なし) ---
    def get_cpu_params(self):
        params = {
            1:  {'d': 0, 'm': 0.5, 'g': 20, 'f': False},
            2:  {'d': 0, 'm': 0.3, 'g': 15, 'f': False},
            3:  {'d': 1, 'm': 0.2, 'g': 10, 'f': True},
            4:  {'d': 1, 'm': 0.1, 'g': 8,  'f': True},
            5:  {'d': 1, 'm': 0.05,'g': 5,  'f': True},
            6:  {'d': 2, 'm': 0.0, 'g': 10, 'f': True},
            7:  {'d': 2, 'm': 0.0, 'g': 5,  'f': True},
            8:  {'d': 2, 'm': 0.0, 'g': 2,  'f': True},
            9:  {'d': 3, 'm': 0.0, 'g': 1,  'f': True},
            10: {'d': 3, 'm': 0.0, 'g': 0,  'f': True},
        }
        return params.get(self.level, params[5])

    def evaluate_board(self, board, color, use_full_eval):
        opp = 'white' if color == 'black' else 'black'
        my_stones = [c for c, st in board.items() if st == color]
        opp_stones = [c for c, st in board.items() if st == opp]
        empty_count = list(board.values()).count(None)
        if empty_count < 12:
            return (len(my_stones) - len(opp_stones)) * 100
        if not use_full_eval:
            return len(my_stones) - len(opp_stones)
        score = 0
        for coord in my_stones:
            val = 1
            if coord in CIRCUMFERENCE:
                val += 10
                if coord in STRATEGIC_NODES: val += 15
            elif coord in [(3,3), (3,4), (4,3), (4,4)]: val -= 5
            score += val
        for coord in opp_stones:
            val = 1
            if coord in CIRCUMFERENCE:
                val += 10
                if coord in STRATEGIC_NODES: val += 15
            elif coord in [(3,3), (3,4), (4,3), (4,4)]: val -= 5
            score -= val
        my_lib, opp_lib = 0, 0
        for coord, st in board.items():
            if st is None: continue
            libs = 0
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                n = (coord[0]+dx, coord[1]+dy)
                if n in VALID_COORDS and board[n] is None: libs += 1
            if st == color: my_lib += libs
            else: opp_lib += libs
        score += (opp_lib * 3) - (my_lib * 3)
        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing, color, use_full_eval):
        if depth == 0:
            return self.evaluate_board(board, color, use_full_eval)
        current_player = color if is_maximizing else ('white' if color == 'black' else 'black')
        moves = [n for n in VALID_COORDS if self.get_flipped(n, current_player, board)]
        if not moves:
            opp = 'white' if current_player == 'black' else 'black'
            opp_moves = any(self.get_flipped(n, opp, board) for n in VALID_COORDS)
            if not opp_moves: return self.evaluate_board(board, color, True)
            return self.minimax(board, depth-1, alpha, beta, not is_maximizing, color, use_full_eval)
        if is_maximizing:
            v = -1000000
            for m in moves:
                nb = board.copy()
                nb[m] = color
                for f in self.get_flipped(m, color, board):
                    if f != (99,99): nb[f] = color
                v = max(v, self.minimax(nb, depth-1, alpha, beta, False, color, use_full_eval))
                alpha = max(alpha, v)
                if beta <= alpha: break
            return v
        else:
            v = 1000000
            opp = 'white' if color == 'black' else 'black'
            for m in moves:
                nb = board.copy()
                nb[m] = opp
                for f in self.get_flipped(m, opp, board):
                    if f != (99,99): nb[f] = opp
                v = min(v, self.minimax(nb, depth-1, alpha, beta, True, color, use_full_eval))
                beta = min(beta, v)
                if beta <= alpha: break
            return v

    def cpu_move(self):
        moves = []
        for n in VALID_COORDS:
            f = self.get_flipped(n, self.turn, self.board)
            if f: moves.append((n, f))
        if not moves: return
        empty_count = list(self.board.values()).count(None)
        p = self.get_cpu_params()
        current_depth = p['d']
        if empty_count <= 6: current_depth = 12
        elif empty_count <= 12: current_depth = max(current_depth, 4)
        stone_count = sum(1 for v in self.board.values() if v is not None)
        if self.turn == 'white' and stone_count == 5:
            best_m = random.choice(moves)[0]
        elif empty_count > 6 and random.random() < p['m'] and len(moves) > 1:
            best_m = random.choice(moves)[0]
        else:
            scored_moves = []
            for m, f in moves:
                nb = self.board.copy()
                nb[m] = self.turn
                for s in f:
                    if s != (99,99): nb[s] = self.turn
                v = self.minimax(nb, current_depth, -1000000, 1000000, False, self.turn, p['f'])
                scored_moves.append((m, v))
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            best_v = scored_moves[0][1]
            margin = 0 if empty_count <= 6 else p['g']
            candidates = [m for m, v in scored_moves if v >= (best_v - margin)]
            best_m = random.choice(candidates)
        self.make_move(best_m)

    # --- ゲームロジック ---
    def get_flipped(self, start, color, board_state):
        if board_state[start] is not None: return []
        opp = 'white' if color == 'black' else 'black'
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
        circle_flipped = []
        is_last_circum_piece = False
        has_my_stone_on_circum = False
        if start in CIRCUMFERENCE:
            for node in CIRCUMFERENCE:
                if node != start and board_state[node] == color:
                    has_my_stone_on_circum = True
                    break
            empty_on_circum = [n for n in CIRCUMFERENCE if board_state[n] is None]
            if len(empty_on_circum) == 1: is_last_circum_piece = True
            idx = CIRCUMFERENCE.index(start)
            circle = CIRCUMFERENCE[idx:] + CIRCUMFERENCE[:idx]
            if all(board_state[n] == opp for n in circle[1:]):
                if has_my_stone_on_circum: circle_flipped.extend(circle[1:])
            else:
                for d in [1, -1]:
                    path = []
                    for i in range(1, len(circle)):
                        curr = circle[(i * d) % len(circle)]
                        st = board_state[curr]
                        if st == opp: path.append(curr)
                        elif st == color:
                            circle_flipped.extend(path)
                            break
                        else: break
        total = list(set(normal_flipped + circle_flipped))
        if is_last_circum_piece:
            if normal_flipped or has_my_stone_on_circum: return total if total else [(99,99)]
            return []
        return total if total else []

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
            self.last_move = coord  # ここで更新
            for n in to_flip:
                if n in VALID_COORDS: self.board[n] = self.turn
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.draw_board()
            self.root.after(100, self.check_pass)

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

    def reset_game(self):
        self.board = {coord: None for coord in VALID_COORDS}
        self.board[(3,3)], self.board[(4,4)] = 'white', 'white'
        self.board[(4,3)], self.board[(3,4)] = 'black', 'black'
        self.turn = 'black'
        self.last_move = None
        self.history = []
        self.draw_board()
        if self.mode == "PvE" and self.turn == self.cpu_color: self.root.after(600, self.cpu_move)

    def undo(self):
        if not self.history: return
        steps = 2 if self.mode == "PvE" else 1
        for _ in range(steps):
            if self.history:
                s = self.history.pop()
                self.board, self.turn = s['board'], s['turn']
                self.last_move = s.get('last_move')
        self.draw_board()

    def update_status(self):
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        txt = f"黒: {b}  白: {w} | 次: {'黒' if self.turn == 'black' else '白'}"
        if self.mode == "PvE": txt += f" (Lv{self.level})"
        self.label_status.config(text=txt)

    def end_game(self):
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        res = "引き分け" if b==w else ("黒の勝ち！" if b>w else "白の勝ち！")
        messagebox.showinfo("終局", f"スコア\n黒: {b}  白: {w}\n{res}")

if __name__ == "__main__":
    root = tk.Tk()
    game = NipGame(root)
    root.mainloop()
    