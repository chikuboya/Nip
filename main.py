from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
import os

# フォント登録（font.ttcがリポジトリにある前提）
font_path = os.path.join(os.path.dirname(__file__), 'font.ttc')
if os.path.exists(font_path):
    LabelBase.register(DEFAULT_FONT, font_path)

class NipGameRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 背景色（緑）
        with self.canvas.before:
            Color(0.2, 0.4, 0.2, 1)
            self.rect = Line(rectangle=(0, 0, Window.width, Window.height)) # 簡易背景
            
        # タイトル
        self.add_widget(Label(
            text="NIP 円形オセロ (Kivy版)",
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(1, 0.1),
            font_size='24sp'
        ))

        # テスト用ボタン
        btn = Button(
            text="対局開始（テスト）",
            size_hint=(0.6, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(btn)

class NipApp(App):
    def build(self):
        return NipGameRoot()

if __name__ == '__main__':
    NipApp().run()
