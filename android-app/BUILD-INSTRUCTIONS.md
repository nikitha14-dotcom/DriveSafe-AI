# DriveSafe Android app source

## Build an APK in Android Studio

1. In Android Studio choose **Open** and select `E:\DriveSafe-AI\android-app`.
2. Let Gradle sync. The project wrapper now selects Gradle 8.10.2, required by the Android Gradle Plugin 8.8.0. If Android Studio is set to a local Gradle install, change **Settings > Build, Execution, Deployment > Build Tools > Gradle > Distribution** to use the project wrapper.
3. If asked, install Android SDK Platform 35 and Build Tools using Android Studio's SDK Manager.
4. Select **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
5. Android Studio will show **Locate** when the build completes. The APK is at `app\build\outputs\apk\debug\app-debug.apk`.
6. Copy that APK to the Android phone, open it, and allow installation when Android asks.
7. Start DriveSafe on the PC with LAN access enabled; make sure both devices use the same Wi-Fi. In the phone app, enter the PC's Wi-Fi IPv4 address.

You can also build from Command Prompt with `cd /d E:\DriveSafe-AI\android-app` followed by `gradlew.bat assembleDebug`.

This is a debug APK for direct installation. The app does not run camera AI on the phone; the PC continues doing that and serves the dashboard to the phone over your local Wi-Fi.
