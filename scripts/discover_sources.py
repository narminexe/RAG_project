r"""
PHASE 1.1 - Source inventory. Discovers what exists on dp.edu.az.
Does NOT build the corpus - it only catalogues, so we can decide what to keep.
"""
import csv, re, time, pathlib, requests
from bs4 import BeautifulSoup

BASE = "https://dp.edu.az"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
SEEDS = ["/az/index", "/az/faq", "/az/content/78", "/az/content/79", "/az/content/5",
         "/az/content/17", "/az/content/53", "/az/content/81"]

seen_pages, files, rows = set(), {}, []
queue = list(SEEDS)

while queue:
    path = queue.pop(0)
    if path in seen_pages:
        continue
    seen_pages.add(path)
    try:
        r = requests.get(BASE + path, headers=HEADERS, timeout=30)
        r.encoding = "utf-8"
        if r.status_code != 200:
            continue
    except Exception:
        continue
    time.sleep(1)

    soup = BeautifulSoup(r.text, "lxml")
    desc = soup.select_one("div.desc")
    text = desc.get_text(" ", strip=True) if desc else ""
    title = (soup.find("h1") or soup.find("h2"))
    rows.append({"doc_id": "dp" + path.replace("/az", "").replace("/", "-"),
                 "url": BASE + path, "type": "html",
                 "title": (title.get_text(strip=True) if title else "")[:70],
                 "chars": len(text)})

    for a in soup.find_all("a", href=True):
        href, label = a["href"].strip(), " ".join(a.get_text(" ", strip=True).split())[:70]
        if re.match(r"^/az/content/\d+$", href) and href not in seen_pages:
            queue.append(href)
        elif re.search(r"\.(pdf|xlsx|docx)$", href, re.I):
            full = href if href.startswith("http") else BASE + href
            files.setdefault(full, label)

for url, label in files.items():
    rows.append({"doc_id": "file-" + url.rsplit("/", 1)[-1][:12], "url": url,
                 "type": url.rsplit(".", 1)[-1].lower(), "title": label, "chars": ""})

pathlib.Path("data").mkdir(exist_ok=True)
with open("data/sources.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["doc_id", "url", "type", "title", "chars"])
    w.writeheader(); w.writerows(rows)

html = [r for r in rows if r["type"] == "html"]
print(f"HTML pages found: {len(html)}   files found: {len(files)}")
print(f"written -> data/sources.csv")
