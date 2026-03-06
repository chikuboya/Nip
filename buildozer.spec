[app]
title = Nip
package.name = nip
package.domain = org.chikuboya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttc
version = 0.1

icon.filename = %(source.dir)s/icon.png

requirements = python3,kivy==2.3.0,pillow,kivmob

orientation = portrait
fullscreen = 1

android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# AdMob SDK
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0

# AdMob テストアプリID
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
