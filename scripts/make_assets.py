"""Build launcher icons + splash screens from your own logo.png (repo root).
Runs in CI after `cap add android`. If logo.png is missing it does nothing."""
import pathlib, re, sys
from PIL import Image

BG = "#070F1C"            # icon / splash background colour - change here if you like
LOGO = pathlib.Path("logo.png")
RES = pathlib.Path("android/app/src/main/res")

if not LOGO.exists():
    print("logo.png not found - keeping default icons"); sys.exit(0)

def hex2rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
bg = hex2rgb(BG)

# make the logo square (pad, never crop)
src = Image.open(LOGO).convert("RGBA")
side = max(src.size)
logo = Image.new("RGBA", (side, side), (0, 0, 0, 0))
logo.paste(src, ((side - src.width) // 2, (side - src.height) // 2))

def fit(size, scale):
    s = max(1, int(size * scale))
    return logo.resize((s, s), Image.LANCZOS)

def canvas(w, h, color=None):
    return Image.new("RGBA", (w, h), (*color, 255) if color else (0, 0, 0, 0))

def place(base, img):
    base.alpha_composite(img, ((base.width - img.width) // 2, (base.height - img.height) // 2)); return base

legacy = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
adaptive = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
for d in legacy:
    folder = RES / f"mipmap-{d}"
    if not folder.exists(): continue
    n = legacy[d]
    sq = place(canvas(n, n, bg), fit(n, 0.82))
    sq.convert("RGBA").save(folder / "ic_launcher.png")
    rnd = place(canvas(n, n, bg), fit(n, 0.70))
    mask = Image.new("L", (n, n), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).ellipse((0, 0, n - 1, n - 1), fill=255)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0)); out.paste(rnd, (0, 0), mask); out.save(folder / "ic_launcher_round.png")
    a = adaptive[d]
    place(canvas(a, a), fit(a, 0.62)).save(folder / "ic_launcher_foreground.png")

# icon background colour (adaptive icon + Android 12 splash)
bgxml = RES / "values/ic_launcher_background.xml"
if bgxml.exists():
    bgxml.write_text(re.sub(r"#[0-9A-Fa-f]{6}", BG, bgxml.read_text(encoding="utf-8")), encoding="utf-8")

# old-style splash images (Android 11 and below): keep each file's size, draw logo in the middle
for f in RES.glob("drawable*/splash.png"):
    w, h = Image.open(f).size
    place(canvas(w, h, bg), fit(min(w, h), 0.40)).convert("RGB").save(f)

# Android 12+ splash icon + theme
(RES / "drawable").mkdir(exist_ok=True)
place(canvas(768, 768), fit(768, 0.60)).save(RES / "drawable/splash_icon.png")
st = RES / "values/styles.xml"
t = st.read_text(encoding="utf-8")
if "windowSplashScreenAnimatedIcon" not in t:
    t = t.replace('<item name="android:background">@drawable/splash</item>',
                  '<item name="android:background">@drawable/splash</item>\n'
                  '        <item name="windowSplashScreenBackground">@color/ic_launcher_background</item>\n'
                  '        <item name="windowSplashScreenAnimatedIcon">@drawable/splash_icon</item>', 1)
    st.write_text(t, encoding="utf-8")
print("icons + splash generated from logo.png")
