r"""
SPIKE STEP 3 - Search: given a question, find which chunks answer it.

This is the retrieval step. No LLM is involved - on purpose. A fluent LLM answer
hides bad retrieval, so we look at the raw chunks and their scores first.

Run:  .venv\Scripts\python.exe spike\03_search.py "your question here"
"""
import sys
import json
import pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

# Azerbaijani-specialised retrieval model, fine-tuned from multilingual-e5-small
# on 3.5M Azerbaijani query-passage pairs. Chosen because ~97% of real questions
# will be Azerbaijani. See DECISIONS.md D-001.
MODEL_NAME = "LocalDoc/LocRet-small"

question = sys.argv[1] if len(sys.argv) > 1 else "IELTS-dən minimum neçə bal tələb olunur?"

chunks = json.loads(pathlib.Path("data/processed/spike_chunks.json")
                    .read_text(encoding="utf-8"))

print(f"loading model {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)

# This model family needs to be told whether it is reading a QUESTION or a
# DOCUMENT. LocRet declares both prefixes in its own config, so we pass
# prompt_name and let it apply them. Writing "query: " by hand as well would
# double-prefix the text and quietly wreck the scores.
chunk_vectors = model.encode(
    [c["text"] for c in chunks],
    prompt_name="document",
    normalize_embeddings=True,   # scale every vector to length 1 (see below)
)
question_vector = model.encode([question], prompt_name="query",
                               normalize_embeddings=True)[0]

print(f"{len(chunks)} chunks -> matrix of shape {chunk_vectors.shape}")
print(f"   ({chunk_vectors.shape[0]} chunks, "
      f"{chunk_vectors.shape[1]} numbers describing each one)\n")

# Because every vector has length 1, the dot product IS cosine similarity:
# 1.0 = same meaning, 0.0 = unrelated. 10 chunks = 10 comparisons, brute force.
scores = chunk_vectors @ question_vector
ranking = np.argsort(-scores)   # minus sign = highest score first

print("=" * 78)
print(f"QUESTION: {question}")
print("=" * 78)
for rank, i in enumerate(ranking, start=1):
    marker = ">>>" if rank <= 3 else "   "
    preview = chunks[i]["text"].replace("\n", " / ")[:95]
    print(f"{marker} #{rank}  score {scores[i]:.4f}  chunk {i:>2} [{chunks[i]['doc_id']}]")
    print(f"        {preview}...")

print("\nTop chunk in full:")
print("-" * 78)
print(chunks[ranking[0]]["text"])
print("-" * 78)
print("source:", chunks[ranking[0]]["url"])
