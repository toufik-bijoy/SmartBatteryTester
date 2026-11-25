"""Run after `npx cap add android`: permissions, keep-screen-on, icon, background colour."""
import pathlib, re, shutil

root = pathlib.Path("android")
app = root / "app/src/main"

# 1) Bluetooth permissions (scan without location on Android 12+)
man = app / "AndroidManifest.xml"
t = man.read_text(encoding="utf-8")
if "xmlns:tools" not in t:
    t = t.replace('xmlns:android="http://schemas.android.com/apk/res/android"',
                  'xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools"', 1)
if "neverForLocation" not in t:
    perms = (
        '    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" android:maxSdkVersion="30" />\n'
        '    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" android:maxSdkVersion="30" />\n'
        '    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation" tools:targetApi="s" />\n'
    )
    t = t.replace("</manifest>", perms + "</manifest>")
man.write_text(t, encoding="utf-8")

# 2) Keep the screen on while the app is open
for f in (app / "java").rglob("MainActivity.*"):
    pkg = re.search(r"package\s+([\w.]+)", f.read_text(encoding="utf-8")).group(1)
    if f.suffix == ".java":
        f.write_text(f"""package {pkg};

import android.os.Bundle;
import android.view.WindowManager;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {{
    @Override
    public void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }}
}}
""", encoding="utf-8")
    elif f.suffix == ".kt":
        f.write_text(f"""package {pkg}

import android.os.Bundle
import android.view.WindowManager
import com.getcapacitor.BridgeActivity

class MainActivity : BridgeActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }}
}}
""", encoding="utf-8")

# 3) Launcher icons (only overwrite files that exist)
res = app / "res"
for src in pathlib.Path("android-res").rglob("*.png"):
    dst = res / src.relative_to("android-res")
    if dst.exists():
        shutil.copy(src, dst)
bg = res / "values/ic_launcher_background.xml"
if bg.exists():
    bg.write_text(re.sub(r"#[0-9A-Fa-f]{6}", "#070F1C", bg.read_text(encoding="utf-8")), encoding="utf-8")
print("android patched")
