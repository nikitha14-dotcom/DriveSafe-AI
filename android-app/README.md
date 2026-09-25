# DriveSafe AI for Android

This Android app opens the DriveSafe dashboard in an installable app window. The PC still runs the camera and AI detector; both devices must be on the same Wi-Fi network, and the PC app must be running. The APK has not been built or device-tested yet.

## Install

Install `app/build/outputs/apk/debug/app-debug.apk` on the Android phone. Android may ask you to allow installation from the file manager or browser used to open the APK. Open **DriveSafe AI**, enter the PC's private Wi-Fi IPv4 address, then tap **Connect**. The app remembers that address.

## Find the PC address

On Windows, run `ipconfig` in Command Prompt and find the IPv4 Address under the Wi-Fi adapter (for example `192.168.1.24`). In the PC project folder, start the dashboard-enabled DriveSafe server with its LAN option enabled (`DRIVESAFE_LAN=1`) and allow Python through Windows Firewall on **Private networks** when prompted. The server must listen on port 5000.

This APK is a debug build for direct installation. A Play Store release would need a separately signed release build.
