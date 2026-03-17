[app]

# アプリ基本情報
title = Nip
package.name = nip
package.domain = org.chikuboya

# ソース
source.dir = .
source.include_exts = py,png,jpg,ttc

# バージョン
version = 0.1

# アイコン
icon.filename = %(source.dir)s/icon.png

# 必須ライブラリ
requirements = python3,kivy==2.3.0,pillow,kivmob

# 画面設定
orientation = portrait
fullscreen = 1

# 権限（AdMob用）
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# API設定（重要）
android.api = 33
android.minapi = 21

# AdMob用設定（kivmob必須）
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0

# ビルド高速化
android.accept_sdk_license = True

# ログレベル
log_level = 2

# 起動ファイル
entrypoint = main.py

# パッケージに含めるファイル
source.include_patterns = assets/*,images/*,*.ttc

# 日本語フォント対応（今回重要）
android.add_assets = font.ttc

# デバッグ時ログ
android.logcat_filters = *:S python:D

# フルスクリーン安定化
android.presplash_color = #FFFFFF

# 64bit対応
android.archs = arm64-v8a, armeabi-v7a
