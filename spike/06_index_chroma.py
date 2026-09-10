r"""
SPIKE STEP 6 - Build the vector store (tutorial step 4).

Embed every chunk ONCE and save the vectors to disk in Chroma.
Compare with 03_search.py, which re-embeds all chunks on every single run and
throws the result away when the script exits.

IMPORTANT: Chroma has a built-in embedding model (all-MiniLM-L6-v2) and it is
ENGLISH-ONLY. If we let Chroma embed for us, Azerbaijani retrieval would be
garbage. So we embed with LocRet ourselves and hand Chroma the finished vectors.

Run:  .venv\Scripts\python.exe spike\06_index_chroma.py
"""
import json
import pathlib
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "data/chroma"
COLLECTION = "dp_chunks"
MODEL_NAME = "LocalDoc/LocRet-small"   # see DECISIONS.md D-002

chunks = json.loads(pathlib.Path("data/processed/spike_chunks.json")
                    .read_text(encoding="utf-8"))

print(f"loading {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)

# The expensive step. From now on it happens once, not once per search.
print(f"embedding {len(chunks)} chunks ...")
# SEARCH on the clean chunk ("body"). The 300-char context prefix is mostly
# identical legal boilerplate, so embedding it made chunks look alike and pushed
# IELTS answers from rank 1-2 down to rank 6-7. The prefixed "text" is still
# stored below, so the MODEL sees the context when it writes the answer.
vectors = model.encode([c["body"] for c in chunks],
                       prompt_name="document",
                       normalize_embeddings=True)

# PersistentClient writes to disk. EphemeralClient would vanish on exit -
# which is exactly the problem we are fixing.
client = chromadb.PersistentClient(path=DB_DIR)

# Start clean so re-running this script never leaves stale chunks behind.
if COLLECTION in [c.name for c in client.list_collections()]:
    client.delete_collection(COLLECTION)

# "hnsw:space": "cosine" makes Chroma measure distance the same way
# 03_search.py did. The default is squared L2, which would give different
# numbers and quietly break any comparison between the two scripts.
collection = client.create_collection(
    name=COLLECTION,
    metadata={"hnsw:space": "cosine"},
)

collection.add(
    ids=[f"chunk-{i}" for i in range(len(chunks))],
    embeddings=[v.tolist() for v in vectors],
    documents=[c["text"] for c in chunks],        # Chroma stores the text too
    metadatas=[{"doc_id": c["doc_id"], "url": c["url"]} for c in chunks],
)

print(f"\nstored {collection.count()} chunks in {DB_DIR}/")
print("this directory is gitignored - it is a build artefact, rebuilt by this script")
