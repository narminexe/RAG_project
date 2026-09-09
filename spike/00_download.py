r"""
SPIKE STEP 0 - Download the source pages from dp.edu.az.

Reads the page list from data/sources.csv (built by scripts/discover_sources.py)
instead of a hardcoded list, so extending the corpus means editing a CSV.

Run:  .venv\Scripts\python.exe spike\00_download.py
"""
import csv
import time
import pathlib
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
OUT_DIR = pathlib.Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

pages = [r for r in csv.DictReader(open("data/sources.csv", encoding="utf-8"))
         if r["type"] == "html" and int(r["chars"] or 0) > 200]   # skip empty shells

print(f"{len(pages)} html pages in the inventory\n")
downloaded = skipped = 0

for row in pages:
    out_path = OUT_DIR / f"{row['doc_id']}.html"

    # Never download twice. You re-run this constantly during development.
    if out_path.exists():
        skipped += 1
        continue

    response = requests.get(row["url"], headers=HEADERS, timeout=30)
    response.raise_for_status()   # crash loudly on 404/500 rather than saving an error page
    response.encoding = "utf-8"   # force UTF-8 so Azerbaijani letters survive
    out_path.write_text(response.text, encoding="utf-8")
    downloaded += 1
    print(f"  saved {row['doc_id']:<22} {len(response.text):>7,} chars  {row['title'][:40]}")
    time.sleep(1)                 # one request per second - be a polite guest

print(f"\ndownloaded {downloaded}, already on disk {skipped}")
