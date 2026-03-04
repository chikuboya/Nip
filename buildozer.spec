[app]
title = Nip
package.name = nip
package.domain = org.chikuboya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttc
version = 0.1

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# ★ 依存関係を最小限かつ確実に
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# ★ Android SDK/NDK のバージョンを安定版に固定
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# ★ ログを詳細に出す設定に変更
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

