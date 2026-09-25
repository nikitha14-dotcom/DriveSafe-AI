# DriveSafe Android app source

## Build an APK in Android Studio

1. Extract this folder.
2. In Android Studio choose **Open** and select the extracted `DriveSafe-Android` folder.
3. Let Gradle sync finish. If asked, install Android SDK Platform 35 and Build Tools using Android Studio's SDK Manager.
4. Select **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
5. Android Studio will show the APK location, normally `app/build/outputs/apk/debug/app-debug.apk`.
6. Copy that APK to the Android phone, open it, and allow installation when Android asks.
7. Start DriveSafe on the PC with LAN access enabled; make sure both devices use the same Wi-Fi. In the phone app, enter the PC's Wi-Fi IPv4 address.

This is a debug APK for direct installation. The app does not run camera AI on the phone; the PC continues doing that and serves the dashboard to the phone over your local Wi-Fi.
