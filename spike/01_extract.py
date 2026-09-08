r"""
SPIKE STEP 1 - Turn saved HTML into clean Azerbaijani text.

Run:  .venv\Scripts\python.exe spike\01_extract.py
"""
import json
import pathlib
from bs4 import BeautifulSoup

# doc_id -> (file on disk, original address)
# The URL is carried along so the chatbot can later cite where an answer came from.
PAGES = {
    "dp-content-65": ("data/raw/content_65.html", "https://dp.edu.az/az/content/65"),
    "dp-content-68": ("data/raw/content_68.html", "https://dp.edu.az/az/content/68"),
    "dp-content-76": ("data/raw/content_76.html", "https://dp.edu.az/az/content/76"),
}

documents = []

for doc_id, (path, url) in PAGES.items():
    html = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")

    # BeautifulSoup parses the HTML into a tree we can search.
    soup = BeautifulSoup(html, "lxml")

    # The real content of every dp.edu.az page lives inside <div class="desc">.
    # Everything else on the page is menu, header, footer, social icons - noise
    # that would otherwise end up in our chunks and pollute every search.
    content = soup.select_one("div.desc")

    # A <br> tag is a line break on screen but invisible to get_text().
    # Swap each one for a real newline so list items don't fuse together.
    for br in content.find_all("br"):
        br.replace_with("\n")

    # Pull out the human-readable text, putting a newline between block elements.
    text = content.get_text("\n", strip=True)

    # Collapse the result: drop blank lines and trim stray spaces.
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    text = "\n".join(lines)

    documents.append({"doc_id": doc_id, "url": url, "text": text})
    print(f"{doc_id}  ->  {len(text):,} characters of text")

out = pathlib.Path("data/processed/spike_docs.json")
out.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nsaved {out}")
