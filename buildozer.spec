[app]
# (str) Title of your application
title = Nip

# (str) Package name
package.name = nip

# (str) Package domain (needed for android packaging)
package.domain = org.chikuboya

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttc

# (str) Application version
version = 0.1

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# ★必須変更1：kivmob, android, pyjnius を追加
requirements = python3,kivy==2.3.0,pillow,kivmob,android,pyjnius

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# --- Android specific ---

# ★必須変更2：広告通信のための権限を追加
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# ★必須変更3：AdMob アプリ ID の設定（これが無いと起動直後に落ちます）
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3649897440139100~8105670662

# (list) The Android architectures to build for.
android.archs = arm64-v8a, armeabi-v7a

# --- Logging ---
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
