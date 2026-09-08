r"""
SPIKE STEP 0 - Download the three source pages from dp.edu.az.

Run:  .venv\Scripts\python.exe spike\00_download.py
"""
import time
import pathlib
import requests

# Which pages to fetch. The key becomes the filename, the value is the address.
PAGES = {
    "content_65": "https://dp.edu.az/az/content/65",  # Secim meyarlari
    "content_68": "https://dp.edu.az/az/content/68",  # Xerclerin maliyyelesdirilmesi
    "content_76": "https://dp.edu.az/az/content/76",  # Ohdelikler
}

# Introduce ourselves honestly as a normal browser. Some sites block clients
# that send no User-Agent at all.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

OUT_DIR = pathlib.Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

for name, url in PAGES.items():
    out_path = OUT_DIR / f"{name}.html"

    # Never download the same page twice. During development you re-run this
    # script constantly; without this line you would hammer their server.
    if out_path.exists():
        print(f"skip   {name}  (already on disk)")
        continue

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()      # crash loudly on 404 / 500 instead of saving garbage
    response.encoding = "utf-8"      # force UTF-8 so Azerbaijani letters survive

    out_path.write_text(response.text, encoding="utf-8")
    print(f"saved  {out_path}  ({len(response.text):,} characters)")

    time.sleep(1)   # one request per second - be a polite guest on their server
