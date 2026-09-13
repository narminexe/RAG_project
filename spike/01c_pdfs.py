r"""
SPIKE STEP 1c - Add the PDFs linked from the dp.edu.az homepage.

Some of the most useful information is not on the web pages but in PDFs linked from
the homepage: the application deadline, the required documents, the monthly cost
norms by country. This step extracts their text and adds each PDF as one more
document, so the rest of the pipeline treats it exactly like a web page.

Chosen after inspecting all 14 PDFs on 2026-09-13:
  added    Seçim meyarları və tələb olunan sənədlər (May 2026): criteria, documents, deadline
  added    Aylıq xərc normaları: monthly cost norms by country (a table - see below)
  added    Doktorantura
  skipped  the April 2026 announcement: an older version of the May document above
  skipped  the university / programme list: covered by the status note in 01b (D-009)

TABLES (D-013): a table read as plain text becomes a stream of numbers,
"41. | Portuqaliya | avro | 1200 | 600 | 450 | 50 | 100 | 42. | Polşa | ...", and the column
names appear only once, at the top of page 1. Search still found the right chunk, but the
PICK step dropped it, because nothing in it said which number is food and which is rent.
So each row of the costs table becomes one sentence that carries its own column names.

Order of the ingestion steps:
  00_download -> 01_extract -> 01b_list_status -> 01c_pdfs -> 02_chunk -> 06_index_chroma
(01_extract rewrites spike_docs.json from scratch, so 01b and 01c must run after it.)

Run:  .venv\Scripts\python.exe spike\01c_pdfs.py
"""
import json
import pathlib
import time

import pymupdf
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "processed" / "spike_docs.json"
CACHE = ROOT / "data" / "raw" / "pdf"                     # gitignored, like all of data/raw
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

# (doc_id, title, link) - to add another PDF later, add one line here.
PDFS = [
    ("pdf-secim-meyarlari-2026", "Seçim meyarları və tələb olunan sənədlər (2026/2027)",
     "https://dp.edu.az/uploads/fileuploads/2026/05/4ec0f92d30d04271886e0bc82fcae744.pdf"),
    ("pdf-ayliq-xerc-normalari", "Aylıq xərc normaları",
     "https://dp.edu.az/uploads/fileuploads/2022/06/cd667437d8d542b6acf5b000bbfff7bb.pdf"),
    ("pdf-doktorantura", "Doktorantura",
     "https://dp.edu.az/uploads/fileuploads/2025/08/1715512f051845178834ccda81b368fc.pdf"),
]

# The same correction as in 01_extract.py (D-011). Keep the two in sync.
CORRECTIONS = {"dp22-26@edu.gov.az": "dp22-28@edu.gov.az"}


def plain_text(pdf):
    lines = [" ".join(line.split()) for page in pdf for line in page.get_text().splitlines()]
    return "\n".join(line for line in lines if line)


def costs_table_as_sentences(pdf):
    """The monthly cost norms table, one self-contained sentence per country row.
    Columns: No | country (city) | currency | monthly norm | housing | food | study materials | other.
    The header rows and the repeated "1 2 3 ... 8" column-number rows are skipped."""
    first_page = pdf[0].get_text().split("Sıra")[0]
    intro = " ".join(first_page.split())                  # the title above the table

    sentences = []
    for page in pdf:
        for table in page.find_tables().tables:
            for raw in table.extract():
                r = [" ".join(str(cell or "").split()) for cell in raw]
                if len(r) < 8 or not r[0].rstrip(".").isdigit() or not r[1] or r[1].isdigit():
                    continue
                _, country, currency, norm, housing, food, study, other = r[:8]
                sentences.append(
                    f"{country} üçün aylıq xərc norması: {norm} {currency}. Bundan yataqxana "
                    f"(mənzil kirayəsi) {housing}, qidalanma {food}, tədris materialları ilə "
                    f"təminat {study}, digər xərclər {other} {currency}.")
    return intro + "\n" + "\n".join(sentences), len(sentences)


CACHE.mkdir(parents=True, exist_ok=True)
new_docs = []
for doc_id, title, url in PDFS:
    path = CACHE / url.rsplit("/", 1)[-1]
    if not path.exists():                                 # never download the same file twice
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        path.write_bytes(response.content)
        time.sleep(1)                                     # polite: one request per second

    pdf = pymupdf.open(path)
    note = ""
    if doc_id == "pdf-ayliq-xerc-normalari":
        text, n_rows = costs_table_as_sentences(pdf)
        note = f"  (table: {n_rows} rows turned into sentences)"
    else:
        text = plain_text(pdf)
    for old, new in CORRECTIONS.items():
        text = text.replace(old, new)

    if len(text) < 200:                                   # a scanned image has no text layer
        print(f"!! {doc_id}: almost no text - scanned image? skipped")
        continue
    new_docs.append({"doc_id": doc_id, "url": url, "title": title, "text": text})
    print(f"{doc_id:<28} {len(pdf):>3} pages  {len(text):>7,} chars{note}")

docs = json.loads(DOCS.read_text(encoding="utf-8"))
docs = [d for d in docs if not d["doc_id"].startswith("pdf-")]   # replace, never duplicate
docs += new_docs
DOCS.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n{len(new_docs)} PDFs added -> {len(docs)} documents in {DOCS.relative_to(ROOT)}")
