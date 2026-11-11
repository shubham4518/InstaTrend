"""Download official Google Noto Sans fonts for multi-lingual Indic typography."""
import os
import requests

FONTS = {
    "NotoSans-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    "NotoSans-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "NotoSansDevanagari-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf",
    "NotoSansTamil-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Bold.ttf",
    "NotoSansTelugu-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Bold.ttf",
}

target_dir = os.path.join("trendbharat", "assets", "fonts")
os.makedirs(target_dir, exist_ok=True)

print(f"Target font directory: {target_dir}")
for name, url in FONTS.items():
    dest = os.path.join(target_dir, name)
    if not os.path.exists(dest):
        print(f"Downloading {name}...")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"Saved {name} ({len(r.content)} bytes)")
        except Exception as e:
            print(f"Error downloading {name}: {e}")
    else:
        print(f"{name} already exists.")
print("Font setup complete.")

