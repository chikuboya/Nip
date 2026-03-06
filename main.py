# --- (上部のインポートや盤面定義はそのまま) ---

class GameScreen(Screen):
    # ... (既存のメソッドはそのまま) ...

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
                # 3で割り切れるときだけ表示
                if app.game_count % 3 == 0:
                    # インタースティシャル広告をロードして表示
                    app.ads.request_interstitial()
                    # ロード時間を考慮して少し待ってから表示（または次に備えてリクエストのみでも可）
                    # ここでは即時表示を試みます
                    app.ads.show_interstitial()
            except Exception as e:
                print(f"DEBUG: Failed to show interstitial: {e}")

class NipApp(App):
    def build(self):
        self.game_count = 0

        # 広告の初期化
        if KIVMOB_AVAILABLE and platform == 'android':
            try:
                # アプリIDの設定
                self.ads = KivMob("ca-app-pub-3649897440139100~8105670662")
                
                # 第2引数を True にしてテストモードを有効化
                self.ads.add_banner("ca-app-pub-3649897440139100/2778302303", True)
                self.ads.add_interstitial("ca-app-pub-3649897440139100/8253990263", True)
                
                # 起動直後ではなく、1秒後に広告読み込みを開始（確実性を上げるため）
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
        try:
            self.ads.request_banner()
            self.ads.show_banner()
            self.ads.request_interstitial() # 最初の対局が終わる前に準備しておく
            print("DEBUG: Ads requested via schedule_once")
        except Exception as e:
            print(f"DEBUG: Ad request failed: {e}")

if __name__ == '__main__':
    NipApp().run()
