r"""
SPIKE STEP 1b - Add a "status note" about the university / programme list.

Real applicants almost never ask "is University X on the list?". They ask
"has the list been published yet?". So instead of indexing the 50-page list
(996 look-alike chunks that would crowd every search), this step checks the
dp.edu.az homepage and writes ONE short note: which academic year's list is
published, the PDF link, the next year's status, the date it was checked, and
WHICH COUNTRIES are on the list.

Why the countries (D-014): without them the bot had nothing to go on and answered
"Yaponiya siyahıda var?" with a confident "yoxdur" - while the list holds 82 Japanese
programmes. Countries are few and change rarely, so one line settles the question.
Universities and programmes are still NOT listed: for those the note points to the PDF.

Order of the ingestion steps:
  00_download -> 01_extract -> 01b_list_status -> 01c_pdfs -> 02_chunk -> 06_index_chroma
(01_extract rewrites spike_docs.json from scratch, so this must run after it.)

The note is only as fresh as the last run - re-run the steps above to refresh it.

Run:  .venv\Scripts\python.exe spike\01b_list_status.py
"""
import datetime
import json
import pathlib
import re
import time

import pymupdf
import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = "https://dp.edu.az/az/index"
DOCS = ROOT / "data" / "processed" / "spike_docs.json"
PDF_CACHE = ROOT / "data" / "raw" / "pdf"                 # gitignored, like all of data/raw
DOC_ID = "dp-status-university-list"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

# Link texts on the homepage that mean "the university / programme list"
LIST_TEXT = re.compile(r"(ixtisasların|universitet və proqramların)\s+siyah", re.IGNORECASE)
YEAR = re.compile(r"(20\d\d)\s*[/-]\s*(20\d\d)")
LEVELS = {"bakalavriat", "magistratura", "doktorantura"}


def countries_on_list(url):
    """Count the programmes per country in the list PDF. Each row of the list is printed as
    separate lines: number, level, country (sometimes on two lines), "University", "Programme".
    So the country is whatever stands between a level word and the first quoted name."""
    PDF_CACHE.mkdir(parents=True, exist_ok=True)
    path = PDF_CACHE / url.rsplit("/", 1)[-1]
    if not path.exists():
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
        time.sleep(1)
    lines = [" ".join(line.split()) for page in pymupdf.open(path) for line in page.get_text().splitlines()]
    lines = [line for line in lines if line]
    counts = {}
    for i, line in enumerate(lines):
        if line.lower() not in LEVELS:
            continue
        parts = []
        for nxt in lines[i + 1:i + 4]:
            if nxt[:1] in "\"“”«":
                break
            parts.append(nxt)
        else:
            continue                                      # no quoted university name follows: not a row
        country = " ".join(parts)
        if 2 < len(country) < 60:
            counts[country] = counts.get(country, 0) + 1
    return counts


response = requests.get(HOME, headers=HEADERS, timeout=30)
response.raise_for_status()                 # crash loudly rather than write a wrong note
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "lxml")

found = {}                                  # pdf link -> academic years named in its link texts
for a in soup.find_all("a", href=True):
    label = " ".join(a.get_text(" ", strip=True).split())
    href = a["href"].strip()
    if href.lower().endswith(".pdf") and LIST_TEXT.search(label):
        url = href if href.startswith("http") else "https://dp.edu.az" + href
        years = found.setdefault(url, set())
        years.update(f"{y1}/{y2}" for y1, y2 in YEAR.findall(label))

checked = datetime.date.today().strftime("%d.%m.%Y")
countries = {}

if found:
    # the newest academic year among all list links ("2026/2027" sorts correctly as text)
    year, url = max((y, u) for u, ys in found.items() for y in (ys or {""}))
    countries = countries_on_list(url)
    if countries:
        country_line = (
            "Siyahıda universitetləri və proqramları olan ölkələr (ölkə - proqram sayı): "
            + "; ".join(f"{c} - {n}" for c, n in sorted(countries.items())) + ".\n"
            "Bu sadalanan ölkələrdən başqa ölkənin universiteti bu siyahıda yoxdur.\n")
    else:
        country_line = ""
    if year:
        start = int(year[:4])
        text = (
            "Universitet və proqramların siyahısı (ixtisasların siyahısı) - dərc olunma vəziyyəti\n"
            f"{year} tədris ili üzrə universitetlərin, təhsil proqramlarının və ixtisasların "
            "siyahısı dp.edu.az saytında dərc olunub.\n"
            f"Siyahının linki (PDF): {url}\n"
            + country_line +
            "Konkret universitetin və ya proqramın siyahıda olub-olmadığını bu PDF-də yoxlamaq olar.\n"
            f"{start + 1}/{start + 2} tədris ili üzrə siyahı saytda hələ dərc olunmayıb.\n"
            f"Bu vəziyyət dp.edu.az saytında {checked} tarixində yoxlanılıb."
        )
    else:
        text = (
            "Universitet və proqramların siyahısı (ixtisasların siyahısı) - dərc olunma vəziyyəti\n"
            "Universitet və proqramların siyahısı dp.edu.az saytında dərc olunub, "
            "amma linkdə tədris ili göstərilməyib.\n"
            f"Siyahının linki (PDF): {url}\n"
            + country_line +
            f"Bu vəziyyət dp.edu.az saytında {checked} tarixində yoxlanılıb."
        )
else:
    url = HOME
    text = (
        "Universitet və proqramların siyahısı (ixtisasların siyahısı) - dərc olunma vəziyyəti\n"
        f"dp.edu.az saytının əsas səhifəsində {checked} tarixində universitet və proqramların "
        "siyahısı tapılmadı.\n"
        "Bir müddət sonra dp.edu.az saytını yenidən yoxlamaq tövsiyə olunur."
    )

docs = json.loads(DOCS.read_text(encoding="utf-8"))
docs = [d for d in docs if d["doc_id"] != DOC_ID]       # replace an old note, never duplicate
docs.append({"doc_id": DOC_ID, "url": url,
             "title": "Universitet və proqramların siyahısı: dərc olunma vəziyyəti", "text": text})
DOCS.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"list links found on the homepage: {len(found)}")
print(f"countries parsed from the list: {len(countries)}, programmes: {sum(countries.values())}")
print(f"saved note as '{DOC_ID}' in {DOCS.relative_to(ROOT)}\n")
print(text)
