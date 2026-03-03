[app]

# (str) アプリのタイトル
title = Nip Strategy

# (str) パッケージ名（英小文字とドットのみ）
package.name = nipstrategy

# (str) ドメイン名（自分の名前など）
package.domain = org.chikuboya

# (str) ソースコードがある場所
source.dir = .

# (list) 含めるファイルの拡張子
# ★フォントファイル(.ttc)をしっかり含めています
source.include_exts = py,png,jpg,kv,atlas,ttc

# (list) 含めるファイル名 (特定のファイルがある場合)
source.include_patterns = font.ttc

# (str) アプリのバージョン
version = 0.1

# (list) 必要なライブラリ
requirements = python3,kivy

# (str) アイコン画像の設定
# ★コメントアウトを外し、icon.png を参照するようにしました
icon.filename = %(source.dir)s/icon.png

# (str) 画面の向き (縦固定)
orientation = portrait

# (bool) フルスクリーンにするかどうか
fullscreen = 1

# (int) Android APIレベル
# 現在のGoogle Play要件に合わせて33〜34あたりが推奨されることが多いですが、
# 汎用性を考慮してご指定の31をベースにします。
android.api = 31
android.minapi = 21

# (list) サポートするアーキテクチャ
# 最近のスマホ向けには arm64-v8a が必須です
android.archs = arm64-v8a, armeabi-v7a

# (bool) 署名済みのAPK/AABを生成するかどうか (デバッグ時は0でOK)
android.debug_artifact = 0
