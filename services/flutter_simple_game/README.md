# flutter_simple_game

A new Flutter project.

## 開発準備（Windows 10 + VSCode）
- flutter を公式サイトからDL、好きな場所に解凍、PATHにbinフォルダを追加
- javaを最新化（Amazon Corret17をDL、JAVA_HOME, PATHに追加、java -versionで確認）、
- Android SDKを公式サイトからDL、c:\Android\cmdline-tools\latestフォルダを作成、binフォルダなどをすべて移動
- Visual Studio 2022を公式サイトからインストール、C++でデスクトップアプリ、C++でモバイルアプリ、を選択
- flutter doctorコマンドで☓が無いことを確認

## Hello World（Web + Windows App）
- cd mono-repo/services
- flutter create flutter_simple_game
- flutter run

## Hello World（Android Emulator）
- cd /c/Android/cmdline-tools/latest/bin
<!-- システムイメージを確認・取得 -->
- ./sdkmanager.bat --list | grep "system-images;"
- export ESYS_IMAGE="system-images;android-34;google_apis;x86_64"
- export ESYS_IMAGE="system-images;android-34;google_apis_playstore;x86_64"
- ./sdkmanager.bat $ESYS_IMAGE
<!-- デバイスを確認・取得 -->
- ./avdmanager.bat list device
- ./avdmanager.bat create avd -n my_avd -k $ESYS_IMAGE --device "pixel_4"
- emulator -avd my_avd
- flutter run # エミュレータ起動中はエミュレータで動作する

## Develop and Testing
- flutter pub get
- flutter run

## Create APK file
- flutter build apk --release
- create apk-file to `build/app/outputs/flutter-apk/app-release.apk`

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
