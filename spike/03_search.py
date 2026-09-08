r"""
SPIKE STEP 3 - Search: given a question, find which chunks answer it.

This is the heart of RAG, and the part that actually fails in practice.
No LLM is involved here. On purpose - your PLAN.md (Phase 2.4) makes you read
raw retrieved chunks before adding generation, because a fluent LLM answer hides
bad retrieval.

Run:  .venv\Scripts\python.exe spike\03_search.py "your question here"
"""
import sys
import json
import pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

# A multilingual embedding model. It has seen Azerbaijani, Russian and English,
# which is why a Russian question can match an Azerbaijani paragraph.
# This is a SPIKE choice - you choose the real one in PLAN.md Phase 2.2.
MODEL_NAME = "intfloat/multilingual-e5-small"

question = sys.argv[1] if len(sys.argv) > 1 else "IELTS-dən minimum neçə bal tələb olunur?"

chunks = json.loads(pathlib.Path("data/processed/spike_chunks.json")
                    .read_text(encoding="utf-8"))

print(f"loading model {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)

# --- Turn every chunk into a list of numbers ("a vector") -------------------
# This model outputs 384 numbers per chunk. Those numbers encode MEANING, not
# spelling: two texts that mean the same thing land close together, even in
# different languages.
#
# The "passage:" / "query:" prefixes are a quirk of the e5 model family - it was
# trained to be told whether it is reading a document or a question.
chunk_vectors = model.encode(
    ["passage: " + c["text"] for c in chunks],
    normalize_embeddings=True,   # scale every vector to length 1 (see below)
)

question_vector = model.encode("query: " + question, normalize_embeddings=True)

print(f"{len(chunks)} chunks -> matrix of shape {chunk_vectors.shape}")
print(f"   (that means {chunk_vectors.shape[0]} chunks, "
      f"{chunk_vectors.shape[1]} numbers describing each one)\n")

# --- Compare the question against every chunk -------------------------------
# Because every vector was normalised to length 1, the dot product IS the cosine
# similarity: 1.0 = identical direction/meaning, 0.0 = unrelated.
# 10 chunks means 10 comparisons. Brute force. No database needed at this size.
scores = chunk_vectors @ question_vector

ranking = np.argsort(-scores)   # minus sign = sort highest score first

print("=" * 78)
print(f"QUESTION: {question}")
print("=" * 78)
for rank, i in enumerate(ranking, start=1):
    marker = ">>>" if rank <= 3 else "   "
    preview = chunks[i]["text"].replace("\n", " / ")[:95]
    print(f"{marker} #{rank}  score {scores[i]:.4f}  chunk {i:>2} [{chunks[i]['doc_id']}]")
    print(f"        {preview}...")
print()
print("Top chunk in full:")
print("-" * 78)
print(chunks[ranking[0]]["text"])
print("-" * 78)
print("source:", chunks[ranking[0]]["url"])
