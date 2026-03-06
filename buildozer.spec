[app]
# アプリの基本情報
title = Nip
package.name = nip
package.domain = org.chikuboya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttc
version = 0.1
icon.filename = %(source.dir)s/icon.png

# 必須ライブラリ: kivmob とその依存関係を追加
requirements = python3,kivy==2.3.0,pillow,android,pyjnius,kivmob

orientation = portrait
fullscreen = 1

# 広告通信に必要な権限
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Android SDK/NDK 設定 (2026年現在の推奨値)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# ★ AdMobアプリIDの設定 (スペースを入れないよう注意)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3649897440139100~8105670662

# 実行ログの出力レベル (デバッグ用)
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
