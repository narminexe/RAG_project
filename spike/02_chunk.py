r"""
SPIKE STEP 2 - Cut the text into chunks, each carrying its document's context.

WHY THE CONTEXT PREFIX EXISTS
A bullet like "...ÜOMG 81 bal və ya ondan yuxarı olması" is useless on its own:
nothing in it says whether it is a bakalavriat or a magistratura rule. The
heading that said "magistratura" ended up in a different chunk, so the model
correctly refused to answer "magistratura üçün ortalama nə qədər olmalıdır".

Fix: prepend the first CONTEXT_CHARS of the parent document to every chunk, so
each chunk states its own scope. Set CONTEXT_CHARS = 0 to turn this off and
measure the difference.

Run:  .venv\Scripts\python.exe spike\02_chunk.py
"""
import json
import pathlib

MAX_CHARS = 400        # target size of the chunk body
CONTEXT_CHARS = 300    # how much of the document opening to prepend. 0 = off

documents = json.loads(pathlib.Path("data/processed/spike_docs.json")
                       .read_text(encoding="utf-8"))

chunks = []

for doc in documents:
    # The document's opening usually states its scope - which degree level,
    # which academic year, which regulation.
    context = " ".join(doc["text"][:CONTEXT_CHARS].split()) if CONTEXT_CHARS else ""

    lines = [line for line in doc["text"].split("\n") if line.strip()]

    bodies, buffer = [], ""
    for line in lines:
        if buffer and len(buffer) + len(line) + 1 > MAX_CHARS:
            bodies.append(buffer)
            buffer = line
        else:
            buffer = f"{buffer}\n{line}" if buffer else line
    if buffer:
        bodies.append(buffer)      # the loop leaves the last chunk unsaved

    for body in bodies:
        chunks.append({
            "doc_id": doc["doc_id"],
            "url": doc["url"],
            "body": body,                                   # the chunk itself
            "text": f"{context}\n---\n{body}" if context else body,   # what gets embedded
        })

out = pathlib.Path("data/processed/spike_chunks.json")
out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

avg = sum(len(c["text"]) for c in chunks) / len(chunks)
print(f"{len(documents)} documents -> {len(chunks)} chunks")
print(f"context prefix: {CONTEXT_CHARS} chars | average chunk now {avg:.0f} chars")
print(f"saved {out}")
