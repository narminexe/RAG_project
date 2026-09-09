r"""
SPIKE STEP 8 - Generation (tutorial step 6). THE LAST PIECE.

Retrieve from Chroma -> build the prompt -> send it to an LLM -> print the
answer with its sources.

Swap the generator by changing PROVIDER below. Retrieval, chunks and prompt stay
identical, which is what makes the comparison fair (PLAN.md Phase 4, exp. 7).

Ollama speaks the OpenAI API format, so both providers use the same client and
the same code path - only base_url and model change.

Run:  .venv\Scripts\python.exe spike\08_answer.py "sualınız"
"""
import os
import re
import sys
import time
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

PROVIDER = "openai"          # <-- the one line to change: "ollama" or "openai"
TOP_K = 3

load_dotenv()
CONFIG = {
    # local, free, offline. api_key is required by the client but ignored by Ollama.
    "ollama": dict(model="qwen3:4b", base_url="http://localhost:11434/v1", api_key="ollama"),
    # paid, fast. Needs OPENAI_API_KEY in .env
    "openai": dict(model="gpt-4o-mini", base_url=None, api_key=os.getenv("OPENAI_API_KEY")),
}
cfg = CONFIG[PROVIDER]
if not cfg["api_key"]:
    sys.exit(f"No API key for provider '{PROVIDER}'. Put it in .env, then re-run.")

# $ per 1M tokens, input/output. Only meaningful for paid providers.
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00)}

question = sys.argv[1] if len(sys.argv) > 1 else "Təqaüd təhsil haqqından əlavə nəyi ödəyir?"

# --- RETRIEVAL: same LocRet model that built the index (DECISIONS.md D-002) ---
embedder = SentenceTransformer("LocalDoc/LocRet-small")
collection = chromadb.PersistentClient(path="data/chroma").get_collection("dp_chunks")
q_vector = embedder.encode([question], prompt_name="query",
                           normalize_embeddings=True)[0].tolist()
found = collection.query(query_embeddings=[q_vector], n_results=TOP_K)

context = "\n\n".join(
    f"[mənbə {n}] {meta['url']}\n{doc}"
    for n, (doc, meta) in enumerate(zip(found["documents"][0], found["metadatas"][0]), 1)
)

# --- AUGMENTATION: glue the found text onto the question ---
prompt = f"""Sən Dövlət Proqramı haqqında suallara cavab verən köməkçisən.

QAYDALAR:
- Yalnız aşağıdakı mətnə əsasən cavab ver.
- Cavab mətndə yoxdursa, "Bu məlumat sənədlərdə yoxdur" de. Heç nə uydurma.
- Sualın dilində cavab ver.
- İstifadə etdiyin mənbənin linkini göstər.

MƏTN:
{context}

SUAL: {question}

CAVAB:"""

# --- GENERATION ---
client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
t0 = time.time()
response = client.chat.completions.create(
    model=cfg["model"],
    messages=[{"role": "user", "content": prompt}],
    temperature=0,   # 0 = as repeatable as possible. A different answer every run
)                    # cannot be measured, and Phase 3 needs to measure it.
elapsed = time.time() - t0

answer = response.choices[0].message.content
# Qwen3 can emit its reasoning inside <think>...</think>. Strip it - the user
# wants the answer, and leaving it in would poison the evaluation metrics.
answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

print("=" * 78)
print("SUAL:", question)
print("=" * 78)
print(answer)
print("-" * 78)

# The "Mənbələr:" footer used to list every RETRIEVED chunk, including ones the
# model never used - two of three links were noise. Removed. The prompt already
# asks the model to cite the source it actually used, inline in the answer.

u = response.usage
print(f"\n{PROVIDER}/{cfg['model']}  |  {elapsed:.1f}s  |  "
      f"{u.prompt_tokens} in + {u.completion_tokens} out tokens")
if cfg["model"] in PRICES:
    pin, pout = PRICES[cfg["model"]]
    cost = u.prompt_tokens / 1e6 * pin + u.completion_tokens / 1e6 * pout
    print(f"cost: ~${cost:.6f} this question  (~${cost*60:.4f} for 60)")
