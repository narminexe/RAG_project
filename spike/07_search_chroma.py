r"""
SPIKE STEP 7 - Search the vector store (tutorial step 5, database version).

Same job as 03_search.py, but the chunk vectors are read from disk instead of
being recomputed. Only the QUESTION gets embedded now - one short string.

Run:  .venv\Scripts\python.exe spike\07_search_chroma.py "your question"
      .venv\Scripts\python.exe spike\07_search_chroma.py "your question" dp-content-65
"""
import sys
import time
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "data/chroma"
COLLECTION = "dp_chunks"
TOP_K = 5

question = sys.argv[1] if len(sys.argv) > 1 else "Dil sertifikatı üzrə hansı səviyyə tələb olunur?"
only_doc = sys.argv[2] if len(sys.argv) > 2 else None   # optional metadata filter

t0 = time.time()
model = SentenceTransformer("LocalDoc/LocRet-small")
collection = chromadb.PersistentClient(path=DB_DIR).get_collection(COLLECTION)
t1 = time.time()

# Only ONE short string is embedded now, not the whole corpus.
q_vector = model.encode([question], prompt_name="query",
                        normalize_embeddings=True)[0].tolist()

# `where` filters on metadata BEFORE the similarity search. This is the feature
# FAISS does not have, and the reason we need it: the academic-year problem.
result = collection.query(
    query_embeddings=[q_vector],
    n_results=TOP_K,
    where={"doc_id": only_doc} if only_doc else None,
)
t2 = time.time()

print("=" * 78)
print(f"QUESTION: {question}")
if only_doc:
    print(f"FILTER:   doc_id = {only_doc}")
print("=" * 78)

for rank, (doc, meta, dist) in enumerate(
        zip(result["documents"][0], result["metadatas"][0], result["distances"][0]), start=1):
    # Chroma reports DISTANCE (smaller = closer). With cosine space,
    # similarity = 1 - distance, which puts it back on 03_search.py's scale.
    similarity = 1 - dist
    print(f"#{rank}  similarity {similarity:.4f}   [{meta['doc_id']}]")
    print(f"    {doc.replace(chr(10), ' / ')[:95]}...")
    print(f"    {meta['url']}")

print(f"\nload model + open db : {t1-t0:.2f} s")
print(f"embed question + search: {t2-t1:.2f} s   <- no corpus re-embedding")
