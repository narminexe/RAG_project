r"""
SPIKE STEP 2 - Cut the text into small chunks.

Throwaway code. In the real project YOU design this (PLAN.md Phase 2.1).
Deliberately naive so the idea is visible.

Why chunk at all?
  1. You cannot paste 40 pages into an LLM prompt.
  2. Even if you could, you want to retrieve PRECISELY. If one chunk = one whole
     document, then every question retrieves the whole document and the search
     step has told you nothing.

Run:  .venv\Scripts\python.exe spike\02_chunk.py
"""
import json
import pathlib

MAX_CHARS = 400   # rough target size for one chunk

documents = json.loads(pathlib.Path("data/processed/spike_docs.json")
                       .read_text(encoding="utf-8"))

chunks = []

for doc in documents:
    lines = [line for line in doc["text"].split("\n") if line.strip()]

    buffer = ""            # the chunk we are currently building up
    for line in lines:
        # Would adding this line push us past the size limit?
        if buffer and len(buffer) + len(line) + 1 > MAX_CHARS:
            # Yes - close off the current chunk and start a fresh one.
            chunks.append({"doc_id": doc["doc_id"], "url": doc["url"], "text": buffer})
            buffer = line
        else:
            # No - append the line to the chunk we are building.
            buffer = f"{buffer}\n{line}" if buffer else line

    # The loop ends with a half-built chunk still in the buffer. Don't lose it.
    if buffer:
        chunks.append({"doc_id": doc["doc_id"], "url": doc["url"], "text": buffer})

out = pathlib.Path("data/processed/spike_chunks.json")
out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"{len(documents)} documents  ->  {len(chunks)} chunks")
print(f"saved {out}\n")
for i, chunk in enumerate(chunks):
    preview = chunk["text"].replace("\n", " / ")[:110]
    print(f"chunk {i:>2}  [{chunk['doc_id']}]  {len(chunk['text']):>3} chars  {preview}...")
