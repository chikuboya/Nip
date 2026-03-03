from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
import os
import math
import random

# 日本語フォント登録
font_path = os.path.join(os.path.dirname(__file__), 'font.ttc')
if os.path.exists(font_path):
    LabelBase.register(DEFAULT_FONT, font_path)

# --- 盤面定義 ---
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

class NipGameRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "PvP"
        self.cpu_color = 'white'
        self.turn = 'black'
        self.board = {coord: None for coord in VALID_COORDS}
        self.history = []
        self.last_move = None
        
        # 初期配置
        self.board[(3,3)], self.board[(4,4)] = 'white', 'white'
        self.board[(4,3)], self.board[(3,4)] = 'black', 'black'

        self.setup_ui()
        Clock.schedule_once(self.draw_board)

    def setup_ui(self):
        # ステータスラベル
        self.status_label = Label(
            text="黒: 2  白: 2 | 次: 黒",
            pos_hint={'center_x': 0.5, 'top': 0.98},
            size_hint=(1, 0.05),
            font_size='20sp'
        )
        self.add_widget(self.status_label)

        # 下部ボタンエリア
        btn_layout = FloatLayout(size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0.02})
        
        undo_btn = Button(text="待った", size_hint=(0.3, 0.8), pos_hint={'x': 0.03, 'y': 0.1})
        undo_btn.bind(on_release=lambda x: self.undo())
        
        reset_btn = Button(text="リセット", size_hint=(0.3, 0.8), pos_hint={'x': 0.35, 'y': 0.1})
        reset_btn.bind(on_release=lambda x: self.reset_game())
        
        pve_btn = Button(text="CPU対戦切替", size_hint=(0.3, 0.8), pos_hint={'x': 0.67, 'y': 0.1})
        pve_btn.bind(on_release=self.toggle_mode)

        btn_layout.add_widget(undo_btn)
        btn_layout.add_widget(reset_btn)
        btn_layout.add_widget(pve_btn)
        self.add_widget(btn_layout)

    def toggle_mode(self, instance):
        self.mode = "PvE" if self.mode == "PvP" else "PvP"
        self.reset_game()

    def get_draw_params(self):
        w, h = Window.size
        side = min(w, h * 0.7)
        margin = side * 0.12
        cell_size = (side - margin * 2) / 7
        offset_x = (w - side) / 2
        offset_y = (h - side) / 2 + h * 0.1
        return offset_x, offset_y, margin, cell_size

    def draw_board(self, *args):
        self.canvas.after.clear()
        off_x, off_y, margin, cell_size = self.get_draw_params()

        with self.canvas.after:
            # 盤面の線
            Color(0, 0, 0, 1)
            for c in VALID_COORDS:
                x1 = off_x + margin + c[0] * cell_size
                y1 = off_y + margin + (7-c[1]) * cell_size # Kivyは下が0なので反転
                for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                    target = (c[0]+dx, c[1]+dy)
                    if target in VALID_COORDS:
                        x2 = off_x + margin + target[0] * cell_size
                        y2 = off_y + margin + (7-target[1]) * cell_size
                        Line(points=[x1, y1, x2, y2], width=1.5)

            # 外円
            cx, cy = Window.width / 2, off_y + margin + 3.5 * cell_size
            Line(circle=(cx, cy, cell_size * 3.8), width=2)

            # 石とガイド
            for coord in VALID_COORDS:
                x = off_x + margin + coord[0] * cell_size
                y = off_y + margin + (7-coord[1]) * cell_size
                stone = self.board[coord]

                if stone:
                    Color(0, 0, 0, 1) if stone == 'black' else Color(1, 1, 1, 1)
                    Ellipse(pos=(x - cell_size*0.4, y - cell_size*0.4), size=(cell_size*0.8, cell_size*0.8))
                    if coord == self.last_move:
                        Color(1, 0, 0, 1)
                        Line(circle=(x, y, cell_size*0.4), width=2)
                else:
                    # 置ける場所ガイド
                    if self.get_flipped(coord, self.turn, self.board):
                        Color(1, 1, 0.8, 0.5)
                        Ellipse(pos=(x - cell_size*0.2, y - cell_size*0.2), size=(cell_size*0.4, cell_size*0.4))

        self.update_status()

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
                    if path: normal_flipped.extend(path)
                    break
                else: break
                curr = (curr[0]+dx, curr[1]+dy)
        
        circle_flipped = []
        if start in CIRCUMFERENCE:
            idx = CIRCUMFERENCE.index(start)
            for d in [1, -1]:
                path = []
                for i in range(1, len(CIRCUMFERENCE)):
                    curr = CIRCUMFERENCE[(idx + i * d) % len(CIRCUMFERENCE)]
                    st = board_state[curr]
                    if st == opp: path.append(curr)
                    elif st == color:
                        if path: circle_flipped.extend(path)
                        break
                    else: break
        return list(set(normal_flipped + circle_flipped))

    def on_touch_down(self, touch):
        if self.mode == "PvE" and self.turn == self.cpu_color: return
        off_x, off_y, margin, cell_size = self.get_draw_params()
        
        best, min_dist = None, cell_size * 0.6
        for c in VALID_COORDS:
            nx = off_x + margin + c[0] * cell_size
            ny = off_y + margin + (7-c[1]) * cell_size
            d = math.hypot(nx - touch.x, ny - touch.y)
            if d < min_dist:
                min_dist, best = d, c
        
        if best:
            self.make_move(best)
        return super().on_touch_down(touch)

    def make_move(self, coord):
        to_flip = self.get_flipped(coord, self.turn, self.board)
        if to_flip:
            self.history.append({'board': self.board.copy(), 'turn': self.turn, 'last_move': self.last_move})
            self.board[coord] = self.turn
            self.last_move = coord
            for n in to_flip: self.board[n] = self.turn
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.draw_board()
            Clock.schedule_once(self.check_pass, 0.5)

    def check_pass(self, dt):
        moves = [n for n in VALID_COORDS if self.get_flipped(n, self.turn, self.board)]
        if not moves:
            opp = 'white' if self.turn == 'black' else 'black'
            if not any(self.get_flipped(n, opp, self.board) for n in VALID_COORDS):
                self.status_label.text = "終局！"
            else:
                self.turn = opp
                self.draw_board()
                if self.mode == "PvE" and self.turn == self.cpu_color:
                    Clock.schedule_once(lambda dt: self.cpu_move(), 0.8)
        elif self.mode == "PvE" and self.turn == self.cpu_color:
            Clock.schedule_once(lambda dt: self.cpu_move(), 0.8)

    def cpu_move(self):
        moves = []
        for n in VALID_COORDS:
            f = self.get_flipped(n, self.turn, self.board)
            if f: moves.append((n, f))
        if not moves: return

        scored_moves = []
        for m, f in moves:
            score = len(f)
            if m in STRATEGIC_NODES: score += 15
            elif m in CIRCUMFERENCE: score += 5
            scored_moves.append((m, score))
        
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        best_score = scored_moves[0][1]
        best_candidates = [move for move, score in scored_moves if score == best_score]
        self.make_move(random.choice(best_candidates))

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
        steps = 2 if self.mode == "PvE" and len(self.history) >= 2 else 1
        for _ in range(steps):
            s = self.history.pop()
            self.board, self.turn, self.last_move = s['board'], s['turn'], s['last_move']
        self.draw_board()

    def update_status(self):
        b = list(self.board.values()).count('black')
        w = list(self.board.values()).count('white')
        t_str = "黒" if self.turn == 'black' else "白"
        self.status_label.text = f"黒: {b}  白: {w} | モード: {self.mode} | 次: {t_str}"

class NipApp(App):
    def build(self):
        return NipGameRoot()

if __name__ == '__main__':
    NipApp().run()
