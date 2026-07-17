[app]
title = Vodafone Charge
package.name = vodafonecharge
package.domain = org.mostafa
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt
version = 0.1
requirements = python3,kivy,requests,urllib3,charset-normalizer,certifi,idna
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21
android.private_storage = True
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
p4a.branch = main
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
