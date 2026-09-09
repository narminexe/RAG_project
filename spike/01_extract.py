r"""
SPIKE STEP 1 - Turn saved HTML into clean Azerbaijani text.

Run:  .venv\Scripts\python.exe spike\01_extract.py
"""
import csv
import json
import pathlib
from bs4 import BeautifulSoup

rows = [r for r in csv.DictReader(open("data/sources.csv", encoding="utf-8"))
        if r["type"] == "html" and int(r["chars"] or 0) > 200]

documents, missing, empty = [], [], []

for row in rows:
    path = pathlib.Path("data/raw") / f"{row['doc_id']}.html"
    if not path.exists():
        missing.append(row["doc_id"])
        continue

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")

    # The real content of every dp.edu.az page lives in <div class="desc">.
    # Everything else is menu, header, footer - noise that would pollute chunks.
    content = soup.select_one("div.desc")
    if content is None:
        empty.append(row["doc_id"])       # report it, do not silently skip
        continue

    for br in content.find_all("br"):     # <br> is invisible to get_text()
        br.replace_with("\n")

    text = content.get_text("\n", strip=True)
    text = "\n".join(l.strip() for l in text.split("\n") if l.strip())
    if len(text) < 100:
        empty.append(row["doc_id"])
        continue

    documents.append({"doc_id": row["doc_id"], "url": row["url"],
                      "title": row["title"], "text": text})

documents.sort(key=lambda d: -len(d["text"]))
out = pathlib.Path("data/processed/spike_docs.json")
out.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")

total = sum(len(d["text"]) for d in documents)
print(f"{len(documents)} documents, {total:,} characters total -> {out}\n")
for d in documents[:8]:
    print(f"  {len(d['text']):>6,}  {d['doc_id']:<22} {d['title'][:44]}")
print(f"  ... and {max(0, len(documents)-8)} more")
if empty:   print(f"\nNO USABLE TEXT (check these by hand): {', '.join(empty)}")
if missing: print(f"NOT DOWNLOADED: {', '.join(missing)}")
