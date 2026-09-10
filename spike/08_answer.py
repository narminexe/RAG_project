r"""
SPIKE STEP 8 - Answer a question (tutorial step 6: generation).

What happens when you ask a question, in order:

  1. REWRITE  The LLM writes the question 3 more ways: in the official language of
              the documents, in plain language, and with its most likely meaning
              spelled out. People say "ortalama"; the website says "Ümumi Orta
              Müvəffəqiyyət Göstəricisi". This step bridges the two.
  2. SEARCH   All 4 versions are searched in Chroma and the results are merged. A
              chunk that ranks well for several versions rises to the top.
  3. PICK     The LLM reads the best 25 chunks next to the question and picks the 5
              that really answer it. Search compares blurry summaries; this reads.
  4. ANSWER   The answer model writes the reply from those 5 chunks only - plus short,
              labelled general knowledge where DECISIONS.md D-006 (revised) allows it.

Measured on the same test questions (typos, synonyms, must-refuse controls):
  before: right text in top 5 for 13/19, correct answers 15/21
  now:    right text in top 5 for 18/19, correct answers 20/20
  about 5 seconds and $0.0016 per question. See DECISIONS.md D-005, D-007.

Run:  .venv\Scripts\python.exe spike\08_answer.py "sualınız"
      .venv\Scripts\python.exe spike\08_answer.py "sualınız" --debug
"""
import logging
import os
import pathlib
import re
import sys
import time

# --- quiet start-up ---------------------------------------------------------------
# If LocRet is already downloaded, do not ask HuggingFace about it on every run.
# That lookup hung for minutes when the wifi dropped.
if (pathlib.Path.home() / ".cache/huggingface/hub/models--LocalDoc--LocRet-small").exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TQDM_DISABLE", "1")
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# --- settings ---------------------------------------------------------------------
EMBED_MODEL  = "LocalDoc/LocRet-small"  # must match 06_index_chroma.py (D-002)
SEARCH_MODEL = "gpt-4o-mini"            # steps 1 and 3 - cheap, fast, worked well
ANSWER_MODEL = "gpt-4.1-mini"           # step 4 - best of 4 models tested (D-005)
BASE_URL     = None                     # "http://localhost:11434/v1" = local Ollama

N_REWRITES = 3    # extra versions of the question
PER_QUERY  = 50   # chunks fetched for each version
CANDIDATES = 25   # chunks the LLM reads in step 3
TOP_K      = 5    # chunks the answer model gets

REFUSAL = "Bu məlumat sənədlərdə yoxdur"   # exact text - code will detect it later

# $ per 1M tokens (input, output). Check the OpenAI pricing page - these move.
PRICES = {"gpt-4o-mini": (0.15, 0.60), "gpt-4.1-mini": (0.40, 1.60)}

# --- prompts ----------------------------------------------------------------------
REWRITE_PROMPT = """Bu sual Azərbaycanın xaricdə təhsil üzrə Dövlət Proqramı haqqındadır.
Onu 3 fərqli şəkildə yenidən yaz:
1) Dövlət sənədlərinin rəsmi dilində.
2) Sadə, aydın ədəbi dildə.
3) Sualın ən çox ehtimal olunan mənasını açıq göstərməklə (hansı təhsil səviyyəsi, hansı xərc və s.).
Yeni fakt əlavə etmə. Hər birini ayrı sətirdə yaz, nömrəsiz, başqa heç nə yazma.

Sual: {question}"""

PICK_PROMPT = """Sual: {question}

Aşağıda nömrələnmiş mətn parçaları var. Hansı parçalar bu sualın cavabını ehtiva edir?
Ən uyğun 5 parçanın nömrəsini uyğunluq sırası ilə yaz, yalnız nömrələr, vergüllə: məsələn 3,7,1,12,5

{candidates}"""

ANSWER_PROMPT = """Sən Xaricdə təhsil üzrə Dövlət Proqramı haqqında suallara cavab verən köməkçisən.

İKİ NÖV MƏLUMAT VAR:

1) PROQRAM MƏLUMATI - Dövlət Proqramının qaydaları, tələbləri, tarixləri, məbləğləri,
   sənədləri, kvotaları, universitetləri və öhdəlikləri.
   Bunları YALNIZ aşağıdakı MƏTN-dən götür. Mətndə yoxdursa, öz biliyinlə heç vaxt doldurma.

2) ÜMUMİ MƏLUMAT - Dövlət Proqramının qaydalarında keçən anlayışların qısa izahı (məsələn,
   bir imtahanın, sertifikatın və ya dərəcənin nə olduğu) və standart beynəlxalq
   şkalaların çevrilməsi (məsələn, dil imtahanı balının CEFR səviyyəsinə uyğunluğu).
   Bunu öz biliyinlə 1-2 cümlə ilə verə bilərsən, amma həmin hissənin sonuna mütləq
   "(ümumi məlumat, rəsmi sənəddən deyil)" yaz. Məsləhət (hazırlıq, universitet seçimi
   və s.) vermə.

QAYDALAR:
- İstifadəçi gündəlik sözlər, sinonimlər, qısaltmalar və ya səhv yazılış işlədə bilər.
  Sözlərə yox, MƏNAYA bax.
- Rəqəmi yalnız sualın soruşduğu tələbə aid olduqda işlət. Başqa təhsil səviyyəsinin və
  ya başqa imtahanın rəqəmini cavab kimi vermə.
- İstifadəçi öz nəticəsini deyib bəs edib-etmədiyini soruşursa: cavabı "Bəli" və ya
  "Xeyr" ilə başla, sonra mətndəki tələbi göstər. Müqayisə üçün şkala çevrilməsi
  lazımdırsa, ümumi məlumatdan istifadə et və onu işarələ.
- Sual proqram məlumatı tələb edirsə və o, mətndə yoxdursa, yalnız "Bu məlumat sənədlərdə yoxdur" yaz.
- Sual Dövlət Proqramı ilə əlaqəli deyilsə, yalnız "Bu məlumat sənədlərdə yoxdur" yaz.
- Sualın dilində cavab ver. Qısa və aydın yaz.
- Proqram məlumatı üçün istifadə etdiyin mənbənin linkini göstər.

MƏTN:
{context}

SUAL: {question}

CAVAB:"""

# --- the pipeline -----------------------------------------------------------------
_state = {}


def _setup():
    """Load the models and the index once, on first use."""
    if not _state:
        if BASE_URL is None and not os.getenv("OPENAI_API_KEY"):
            sys.exit("No OPENAI_API_KEY in .env - add it, then re-run.")
        _state["embedder"] = SentenceTransformer(EMBED_MODEL)
        _state["collection"] = (chromadb.PersistentClient(path=str(ROOT / "data" / "chroma"))
                                .get_collection("dp_chunks"))
        _state["llm"] = OpenAI(base_url=BASE_URL, api_key=os.getenv("OPENAI_API_KEY") or "ollama")
    return _state


def _chat(model, prompt, usage):
    """One LLM call. temperature=0 so the same question gives the same answer -
    a different answer every run could not be measured."""
    r = _setup()["llm"].chat.completions.create(
        model=model, temperature=0, messages=[{"role": "user", "content": prompt}])
    tokens = usage.setdefault(model, [0, 0])
    tokens[0] += r.usage.prompt_tokens
    tokens[1] += r.usage.completion_tokens
    text = r.choices[0].message.content or ""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()   # Qwen via Ollama


def rewrite(question, usage):
    """Step 1. The rewrites can contain invented facts (one test rewrite invented
    "75 bal"). That is harmless ONLY because they are used for searching and never
    shown to the user or to the answer model. Keep it that way."""
    raw = _chat(SEARCH_MODEL, REWRITE_PROMPT.format(question=question), usage)
    lines = [re.sub(r"^\s*(\d+[.)]|[-•*])\s*", "", line).strip() for line in raw.splitlines()]
    return [line for line in lines if line][:N_REWRITES]


def search(queries):
    """Step 2. Search every version, merge with reciprocal rank fusion:
    each chunk scores 1/(60 + its rank) per version, and the scores add up."""
    s = _setup()
    vectors = s["embedder"].encode(queries, prompt_name="query", normalize_embeddings=True).tolist()
    found = s["collection"].query(query_embeddings=vectors,
                                  n_results=min(PER_QUERY, s["collection"].count()),
                                  include=["documents", "metadatas"])
    scores, chunks = {}, {}
    for ids, docs, metas in zip(found["ids"], found["documents"], found["metadatas"]):
        for rank, (cid, doc, meta) in enumerate(zip(ids, docs, metas), start=1):
            scores[cid] = scores.get(cid, 0) + 1 / (60 + rank)
            chunks[cid] = (cid, doc, meta)
    best = sorted(scores, key=scores.get, reverse=True)[:CANDIDATES]
    return [chunks[cid] for cid in best]


def pick(question, candidates, usage):
    """Step 3. The LLM reads each candidate next to the question and chooses."""
    listing = "\n\n".join(f"[{n}] {doc[:700]}" for n, (_, doc, _) in enumerate(candidates, 1))
    raw = _chat(SEARCH_MODEL, PICK_PROMPT.format(question=question, candidates=listing), usage)
    chosen = []
    for n in map(int, re.findall(r"\d+", raw)):
        if 1 <= n <= len(candidates) and candidates[n - 1] not in chosen:
            chosen.append(candidates[n - 1])
    return chosen[:TOP_K] or candidates[:TOP_K]   # nonsense reply -> fall back to search order


def answer(question):
    """Question in, answer out. Returns a dict so a UI can use the parts."""
    _setup()
    t0, usage = time.time(), {}
    queries = [question] + rewrite(question, usage)
    chosen = pick(question, search(queries), usage)
    context = "\n\n".join(f"[mənbə {n}] {meta['url']}\n{doc}"
                          for n, (_, doc, meta) in enumerate(chosen, 1))
    text = _chat(ANSWER_MODEL, ANSWER_PROMPT.format(context=context, question=question), usage)
    cost = sum(i / 1e6 * PRICES.get(m, (0, 0))[0] + o / 1e6 * PRICES.get(m, (0, 0))[1]
               for m, (i, o) in usage.items())
    return {
        "answer": text,
        "refused": text.startswith(REFUSAL),
        "sources": list(dict.fromkeys(meta["url"] for _, _, meta in chosen)),
        "queries": queries,
        "chosen": [(cid, meta["doc_id"]) for cid, _, meta in chosen],
        "seconds": time.time() - t0,
        "cost": cost,
    }


if __name__ == "__main__":
    debug = "--debug" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--debug"]
    question = args[0] if args else "magistratura üçün ortalama nə qədər olmalıdır"

    result = answer(question)

    print("=" * 78)
    print("SUAL:", question)
    print("=" * 78)
    print(result["answer"])
    print("-" * 78)
    if debug:
        print("searched with:")
        for q in result["queries"]:
            print("   ", q)
        print("chunks given to the answer model:")
        for cid, doc_id in result["chosen"]:
            print(f"    {cid:<10} {doc_id}")
    print(f"{result['seconds']:.1f}s  |  ~${result['cost']:.5f}  |  answer by {ANSWER_MODEL}")
