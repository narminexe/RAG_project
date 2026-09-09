r"""
SPIKE STEP 4 - Build the prompt.

THIS FILE IS THE ANSWER TO "what does RAG actually do".
It does exactly one thing: glue the found paragraphs onto the question.
That glued-together text is what gets sent to an LLM.

Run:  .venv\Scripts\python.exe spike\04_prompt.py "your question"
"""
import sys, json, pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

TOP_K = 3

question = sys.argv[1] if len(sys.argv) > 1 else "Təqaüd təhsil haqqından əlavə nəyi ödəyir?"

chunks = json.loads(pathlib.Path("data/processed/spike_chunks.json").read_text(encoding="utf-8"))
# Azerbaijani-specialised model - see DECISIONS.md D-001.
model = SentenceTransformer("LocalDoc/LocRet-small")

# prompt_name lets the model apply its own "query: "/"passage: " prefixes.
vectors = model.encode([c["text"] for c in chunks], prompt_name="document",
                       normalize_embeddings=True)
q_vector = model.encode([question], prompt_name="query",
                        normalize_embeddings=True)[0]
best = np.argsort(-(vectors @ q_vector))[:TOP_K]

# Paste the winning chunks into a block of text, each labelled with its source.
context = "\n\n".join(
    f"[source {n}] {chunks[i]['url']}\n{chunks[i]['text']}"
    for n, i in enumerate(best, start=1)
)

prompt = f"""Sən Dövlət Proqramı haqqında suallara cavab verən köməkçisən.

QAYDALAR:
- Yalnız aşağıdakı mətnə əsasən cavab ver.
- Cavab mətndə yoxdursa, "Bu məlumat sənədlərdə yoxdur" de. Uydurma.
- Sualın dilində cavab ver.
- İstifadə etdiyin mənbənin linkini göstər.

MƏTN:
{context}

SUAL: {question}

CAVAB:"""

print(prompt)
