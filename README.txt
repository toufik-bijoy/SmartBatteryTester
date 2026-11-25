SMART BATTERY TESTER - ANDROID APP (offline, native Bluetooth)

Build the APK online (no Android Studio needed):
1. Create a free GitHub account, make a new repository.
2. Upload ALL files of this folder (keep the .github folder).
   If .github does not upload: Add file > Create new file, name it
   .github/workflows/build-apk.yml and paste the contents of that file.
3. Open the Actions tab > "Build APK" > Run workflow. Wait ~5-8 minutes.
4. Open the finished run > Artifacts > download SmartBatteryTester-apk, unzip,
   copy app-debug.apk to the phone and install it (allow "unknown sources").
5. In the app: Device tab > Pair ESP32. Allow "Nearby devices" when asked.

The app works fully offline. Internet is only needed for building.
