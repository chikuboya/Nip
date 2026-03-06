from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
import os
import math
import random
import time

# --- 広告設定 (KivMob) の安全な読み込み ---
KIVMOB_AVAILABLE = False
try:
    if platform == 'android':
        from kivmob import KivMob
        KIVMOB_AVAILABLE = True
except Exception as e:
    print(f"DEBUG: KivMob import failed: {e}")

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
CIRCUMFERENCE = [(0,3), (0,2), (1,1), (2,0), (3,0), (4,0), (5,0), (6,1), (7,2), (7,3), (7,4), (7,5), (6,6), (5,7), (4,7), (3,7), (2,7), (1,6), (0,5), (0,4)]
STRATEGIC_NODES = [(0,3), (7,3), (3,0), (3,7), (0,2), (7,2), (0,5), (7,5)]

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=25)
        layout.add_widget(Label(size_hint_y=0.2)) 
        layout.add_widget(Label(text="NIP ニップ", font_size='35sp', bold=True, size_hint_y=None, height=120))
        
        pvp_btn = Button(text="人 対 人 対局開始", size_hint=(0.8, None), height=100, pos_hint={'center_x': 0.5}, bold=True, font_size='22sp')
        pvp_btn.bind(on_release=lambda x: self.start_game("PvP"))
        layout.add_widget(pvp_btn)
        
        layout.add_widget(Label(text="--- CPU対戦設定 ---", font_size='20sp', size_hint_y=None, height=60, bold=True))
        
        side_layout = BoxLayout(orientation='horizontal', size_hint=(0.8, None), height=80, pos_hint={'center_x': 0.5}, spacing=10)
        self.btn_gote = ToggleButton(text="CPU後手(白)", group='side', state='down', allow_no_selection=False, bold=True, font_size='18sp')
        self.btn_sente = ToggleButton(text="CPU先手(黒)", group='side', allow_no_selection=False, bold=True, font_size='18sp')
        side_layout.add_widget(self.btn_gote)
        side_layout.add_widget(self.btn_sente)
        layout.add_widget(side_layout)
        
        layout.add_widget(Label(text="レベル (1:初心者 - 10:最強)", size_hint_y=None, height=50, bold=True, font_size='18sp'))
        lv_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60, spacing=5)
        self.lv_btns = []
        for i in range(1, 11):
            btn = ToggleButton(text=str(i), group='lv', state='down' if i==5 else 'normal', allow_no_selection=False, bold=True, font_size='16sp')
            self.lv_btns.append(btn)
            lv_layout.add_widget(btn)
        layout.add_widget(lv_layout)
        
        pve_btn = Button(text="人 対 CPU 対局開始", size_hint=(0.9, None), height=120, pos_hint={'center_x': 0.5}, background_color=(0.67, 0.84, 0.9, 1), bold=True, font_size='26sp')
        pve_btn.bind(on_release=lambda x: self.start_game("PvE"))
        layout.add_widget(pve_btn)
        layout.add_widget(Label(size_hint_y=0.3)) 
        self.add_widget(layout)

    def start_game(self, mode):
        app = App.get_running_app()
        app.game_screen.mode = mode
        if mode == "PvE":
            app.game_screen.cpu_color = 'black' if self.btn_sente.state == 'down' else 'white'
            for b in self.lv_btns:
                if b.state == 'down': app.game_screen.level = int(b.text)
        self.manager.current = 'game'
        app.game_screen.reset_game()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = "PvP"
        self.cpu_color = 'white'
        self.level = 5
        self.turn = 'black'
        self.board = {coord: None for coord in VALID_COORDS}
        self.history = []
        self.last_move = None
        self.is_game_over = False 
        self.pass_msg = "" 

        self.main_layout = FloatLayout()
        with self.main_layout.canvas.before:
            Color(143/255, 188/255, 143/255, 1) 
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)

        self.status_label = Label(text="", pos_hint={'center_x': 0.5, 'top': 0.98}, size_hint=(1, 0.1), color=(0,0,0,1), font_size='22sp', bold=True)
        self.main_layout.add_widget(self.status_label)
        self.result_label = Label(text="", pos_hint={'center_x': 0.5, 'top': 0.91}, size_hint=(1, 0.1), font_size='45sp', bold=True, color=(1, 0, 0, 0))
        self.main_layout.add_widget(self.result_label)

        bottom_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0.02}, padding=15, spacing=15)
        btn_undo = Button(text="一手戻る", bold=True, font_size='20sp')
        btn_undo.bind(on_release=lambda x: self.undo())
        btn_reset = Button(text="リセット", bold=True, font_size='20sp')
        btn_reset.bind(on_release=lambda x: self.reset_game())
        btn_menu = Button(text="メニュー", bold=True, font_size='20sp')
        btn_menu.bind(on_release=lambda x: self.go_to_menu())
        
        bottom_box.add_widget(btn_undo)
        bottom_box.add_widget(btn_reset)
        bottom_box.add_widget(btn_menu)
        self.main_layout.add_widget(bottom_box)
        self.add_widget(self.main_layout)
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, *args):
        self.bg_rect.size = Window.size
        self.draw_board()

    def go_to_menu(self):
        self.manager.current = 'menu'

    def get_draw_params(self):
        w, h = Window.size
        board_area_h = h * 0.68 
        canvas_size = min(w, board_area_h)
        margin = canvas_size * 0.12
        cell_size = (canvas_size - margin * 2) / 7
        offset_x = (w - canvas_size) / 2
        offset_y = (h - canvas_size) / 2 - 30 
        return offset_x, offset_y, canvas_size, margin, cell_size

    def draw_board(self, *args):
        self.main_layout.canvas.after.clear()
        off_x, off_y, c_size, margin, cell_size = self.get_draw_params()

        with self.main_layout.canvas.after:
            Color(0, 0, 0, 1)
            for c in VALID_COORDS:
                x1 = off_x + margin + c[0] * cell_size
                y1 = off_y + margin + (7-c[1]) * cell_size
                for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                    target = (c[0]+dx, c[1]+dy)
                    if target in VALID_COORDS:
                        x2 = off_x + margin + target[0] * cell_size
                        y2 = off_y + margin + (7-target[1]) * cell_size
                        Line(points=[x1, y1, x2, y2], width=1.1)
            cx, cy = off_x + c_size/2, off_y + c_size/2
            Line(circle=(cx, cy, cell_size * 3.8), width=1.5)
            for coord in VALID_COORDS:
                x = off_x + margin + coord[0] * cell_size
                y = off_y + margin + (7-coord[1]) * cell_size
                stone = self.board[coord]
                if stone:
                    Color(0, 0, 0, 1) if stone == 'black' else Color(1, 1, 1, 1)
                    Ellipse(pos=(x - cell_size*0.38, y - cell_size*0.38), size=(cell_size*0.76, cell_size*0.76))
                    Color(0.5, 0.5, 0.5, 1)
                    Line(circle=(x, y, cell_size*0.38), width=1)
                    if coord == self.last_move:
                        Color(1, 0, 0, 1)
                        Line(circle=(x, y, cell_size*0.39), width=2)
                else:
                    Color(85/255, 107/255, 47/255, 1)
                    Ellipse(pos=(x - cell_size*0.08, y - cell_size*0.08), size=(cell_size*0.16, cell_size*0.16))
                    if not (self.mode == "PvE" and self.turn == self.cpu_color) and not self.is_game_over:
                        if self.get_flipped(coord, self.turn, self.board):
                            Color(1, 1, 204/255, 0.6)
                            Ellipse(pos=(x - cell_size*0.2, y - cell_size*0.2), size=(cell_size*0.4, cell_size*0.4))
        self.update_status()

    def get_flipped(self, start, color, board_state):
        if board_state[start] is not None: return []
        opp = 'white' if color == 'black' else 'black'
        normal_flipped = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            path, curr = [], (start[0]+dx, start[1]+dy)
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

    def evaluate_board(self, board, color):
        opp = 'white' if color == 'black' else 'black'
        score = 0
        filled = sum(1 for v in board.values() if v is not None)
        is_endgame = filled > 42
        for coord, st in board.items():
            if st is None: continue
            val = 1.0
            if coord in STRATEGIC_NODES: val += 25.0 if not is_endgame else 5.0
            elif coord in CIRCUMFERENCE: val += 10.0 if not is_endgame else 3.0
            if not is_endgame:
                liberties = 0
                for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                    neighbor = (coord[0]+dx, coord[1]+dy)
                    if neighbor in VALID_COORDS and board[neighbor] is None: liberties += 1
                val -= liberties * 1.5
            if is_endgame: val += 5.0
            if st == color: score += val
            else: score -= val
        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing, color):
        if (time.time() - self.start_time > self.time_limit):
            self.abort_search = True
            return self.evaluate_board(board, color)
        if depth == 0 or self.abort_search:
            return self.evaluate_board(board, color)
        opp = 'white' if color == 'black' else 'black'
        curr_p = color if is_maximizing else opp
        moves = []
        for n in VALID_COORDS:
            f = self.get_flipped(n, curr_p, board)
            if f: moves.append((n, f))
        if not moves: return self.evaluate_board(board, color)
        moves.sort(key=lambda x: len(x[1]) + (30 if x[0] in STRATEGIC_NODES else 0), reverse=True)
        if is_maximizing:
            v = -99999
            for m, f in moves:
                nb = board.copy()
                nb[m] = color
                for s in f: nb[s] = color
                res = self.minimax(nb, depth-1, alpha, beta, False, color)
                v = max(v, res)
                alpha = max(alpha, v)
                if beta <= alpha or self.abort_search: break
            return v
        else:
            v = 99999
            for m, f in moves:
                nb = board.copy()
                nb[m] = opp
                for s in f: nb[s] = opp
                res = self.minimax(nb, depth-1, alpha, beta, True, color)
                v = min(v, res)
                beta = min(beta, v)
                if beta <= alpha or self.abort_search: break
            return v

    def cpu_move(self):
        if self.is_game_over: return
        moves = []
        for n in VALID_COORDS:
            f = self.get_flipped(n, self.turn, self.board)
            if f: moves.append((n, f))
        if not moves: return

        my_stones = sum(1 for v in self.board.values() if v == self.cpu_color)
        if my_stones <= 2:
            self.make_move(random.choice(moves)[0])
            return

        lv_cfg = {
            1: {'d': 0, 'r': 0.7, 't': 0.1}, 2: {'d': 1, 'r': 0.5, 't': 0.2},
            3: {'d': 1, 'r': 0.3, 't': 0.3}, 4: {'d': 2, 'r': 0.2, 't': 0.4},
            5: {'d': 2, 'r': 0.1, 't': 0.5}, 6: {'d': 3, 'r': 0.05, 't': 0.7},
            7: {'d': 4, 'r': 0.0, 't': 0.9}, 8: {'d': 6, 'r': 0.0, 't': 1.1},
            9: {'d': 8, 'r': 0.0, 't': 1.3}, 10: {'d': 12, 'r': 0.0, 't': 1.5}
        }
        cfg = lv_cfg.get(self.level, lv_cfg[5])
        
        if random.random() < cfg['r']:
            self.make_move(random.choice(moves)[0])
            return

        self.start_time = time.time()
        self.time_limit = cfg['t']
        self.abort_search = False
        best_m = moves[0][0]

        for d in range(1, cfg['d'] + 1):
            cur_best_v, cur_best_m = -100000, None
            moves.sort(key=lambda x: len(x[1]) + (30 if x[0] in STRATEGIC_NODES else 0), reverse=True)
            for m, f in moves:
                if time.time() - self.start_time > self.time_limit:
                    self.abort_search = True
                    break
                nb = self.board.copy()
                nb[m] = self.turn
                for s in f: nb[s] = self.turn
                val = self.minimax(nb, d-1, -100000, 100000, False, self.turn)
                if val > cur_best_v:
                    cur_best_v, cur_best_m = val, m
            if self.abort_search: break
            else: best_m = cur_best_m
        self.make_move(best_m)

    def on_touch_down(self, touch):
        if touch.y < Window.height * 0.15: return super().on_touch_down(touch)
        if self.is_game_over: return 
        if self.mode == "PvE" and self.turn == self.cpu_color: return
        off_x, off_y, c_size, margin, cell_size = self.get_draw_params()
        best, min_dist = None, cell_size * 0.5
        for c in VALID_COORDS:
            nx = off_x + margin + c[0] * cell_size
            ny = off_y + margin + (7-c[1]) * cell_size
            d = math.hypot(nx - touch.x, ny - touch.y)
            if d < min_dist: min_dist, best = d, c
        if best: self.make_move(best)
        return super().on_touch_down(touch)

    def make_move(self, coord):
        to_flip = self.get_flipped(coord, self.turn, self.board)
        if to_flip:
            self.pass_msg = "" 
            self.history.append({'board': self.board.copy(), 'turn': self.turn, 'last_move': self.last_move})
            self.board[coord] = self.turn
            self.last_move = coord
            for n in to_flip: self.board[n] = self.turn
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.draw_board()
            Clock.schedule_once(self.check_pass, 0.2)

    def check_pass(self, dt):
        moves = [n for n in VALID_COORDS if self.get_flipped(n, self.turn, self.board)]
        if not moves:
            opp = 'white' if self.turn == 'black' else 'black'
            if not any(self.get_flipped(n, opp, self.board) for n in VALID_COORDS):
                self.end_game()
            else:
                p_name = "黒" if self.turn == 'black' else "白"
                self.pass_msg = f"【{p_name}はパスです】"
                self.history.append({'board': self.board.copy(), 'turn': self.turn, 'last_move': self.last_move})
                self.turn = opp
                self.draw_board()
                if self.mode == "PvE" and self.turn == self.cpu_color:
                    Clock.schedule_once(lambda dt: self.cpu_move(), 1.0)
        elif self.mode == "PvE" and self.turn == self.cpu_color:
            Clock.schedule_once(lambda dt: self.cpu_move(), 0.8)

    def reset_game(self):
        self.board = {coord: None for coord in VALID_COORDS}
        self.board[(3,3)], self.board[(4,4)] = 'white', 'white'
        self.board[(4,3)], self.board[(3,4)] = 'black', 'black'
        self.turn = 'black'
        self.last_move = None
        self.history = []
        self.is_game_over = False
        self.pass_msg = ""
        self.result_label.color = (1, 0, 0, 0)
        self.draw_board()
        if self.mode == "PvE" and self.cpu_color == 'black':
            Clock.schedule_once(lambda dt: self.cpu_move(), 1.0)

    def undo(self):
        if not self.history: return
        if self.is_game_over:
            self.is_game_over = False
            self.result_label.color = (1, 0, 0, 0)
        steps = 2 if self.mode == "PvE" and len(self.history) >= 2 else 1
        for _ in range(steps):
            if self.history:
                s = self.history.pop()
                self.board, self.turn, self.last_move = s['board'], s['turn'], s['last_move']
        self.pass_msg = ""
        self.draw_board()

    def update_status(self):
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        t_str = "黒" if self.turn == 'black' else "白"
        status = f"黒: {b}   白: {w} | 次: {t_str}"
        if self.pass_msg: status = f"{self.pass_msg} {status}"
        self.status_label.text = status

    def end_game(self):
        self.is_game_over = True
        b, w = list(self.board.values()).count('black'), list(self.board.values()).count('white')
        winner_text = "黒の勝ち！" if b > w else "白の勝ち！" if w > b else "引き分け"
        self.status_label.text = f"終局: 黒:{b} 対 白:{w}"
        self.result_label.text = winner_text
        self.result_label.color = (1, 0, 0, 1)

        # --- 全画面広告の表示制御 (3回に1回) ---
        if KIVMOB_AVAILABLE and platform == 'android':
            try:
                app = App.get_running_app()
                app.game_count += 1
                if app.game_count % 3 == 0:
                    # 前もってロードされているはずだが、念のためリクエストして表示
                    app.ads.request_interstitial()
                    # ロード待ちを考慮してわずかに遅延させて表示
                    Clock.schedule_once(lambda dt: app.ads.show_interstitial(), 0.5)
            except Exception as e:
                print(f"DEBUG: Failed to show interstitial: {e}")

class NipApp(App):
    def build(self):
        # 対局カウンターの初期化
        self.game_count = 0

        # 広告の初期化
        if KIVMOB_AVAILABLE and platform == 'android':
            try:
                # アプリIDの設定
                self.ads = KivMob("ca-app-pub-3649897440139100~8105670662")
                
                # 第2引数を True にしてテストモードを有効化
                self.ads.add_banner("ca-app-pub-3649897440139100/2778302303", True)
                self.ads.add_interstitial("ca-app-pub-3649897440139100/8253990263", True)
                
                # 起動直後のメインスレッド負荷を下げるため1秒後に読み込み開始
                Clock.schedule_once(self._load_initial_ads, 1)
            except Exception as e:
                print(f"DEBUG: AdMob initialization failed: {e}")

        self.sm = ScreenManager()
        self.menu_screen = MenuScreen(name='menu')
        self.game_screen = GameScreen(name='game')
        self.sm.add_widget(self.menu_screen)
        self.sm.add_widget(self.game_screen)
        return self.sm

    def _load_initial_ads(self, dt):
        """起動時にバナーを表示し、全画面広告を予備ロードしておく"""
        if not (KIVMOB_AVAILABLE and platform == 'android'):
            return
        try:
            self.ads.request_banner()
            self.ads.show_banner()
            # 最初の対局が終わる前に裏で準備（ロード）しておく
            self.ads.request_interstitial() 
            print("DEBUG: Ads requested via schedule_once")
        except Exception as e:
            print(f"DEBUG: Ad request failed: {e}")

if __name__ == '__main__':
    NipApp().run()
