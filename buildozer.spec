[app]
title = Nip Strategy
package.name = nipstrategy
package.domain = org.chikuboya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttc
source.include_patterns = font.ttc
version = 0.1
requirements = python3,kivy

# アイコンは指定せずデフォルトを使用
# icon.filename = %(source.dir)s/icon.png

orientation = portrait
fullscreen = 1
android.api = 31
android.minapi = 21

# ライセンス同意を有効化（これでエラーを回避します）
android.accept_sdk_license = True

# ビルドを軽くするために1つに指定
android.archs = arm64-v8a
android.debug_artifact = 0
