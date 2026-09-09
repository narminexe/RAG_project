r"""
SPIKE STEP 5 - Compare two embedding models on the same questions.

PLAN.md Phase 4 in miniature: change ONE thing (the model), hold everything
else identical, measure.

CAREFUL: models disagree about prefixes. e5 wants you to write "query: " /
"passage: " yourself. LocRet declares them in its config and applies them
automatically - so adding them by hand double-prefixes and tags questions as
documents, which quietly wrecks the comparison. Ask each model what it wants.

Run:  .venv\Scripts\python.exe spike\05_compare.py
"""
import json, pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

MODELS = ["intfloat/multilingual-e5-small", "LocalDoc/LocRet-small"]

GROUND_TRUTH = [
    ("IELTS-dən minimum neçə bal tələb olunur?",            3),
    ("Dil sertifikatı üzrə hansı səviyyə tələb olunur?",    3),
    ("Təqaüd təhsil haqqından əlavə nəyi ödəyir?",          7),
    ("Proqram iştirakçısı ilə müqavilə bağlanılırmı?",      9),
]

chunks = json.loads(pathlib.Path("data/processed/spike_chunks.json").read_text(encoding="utf-8"))
raw_texts = [c["text"] for c in chunks]


def has_prompt(model, name):
    return bool(getattr(model, "prompts", None)) and name in model.prompts


def embed(model, texts, kind):
    """kind is 'query' or 'document'. Use the model's own prompts if it has them."""
    if has_prompt(model, kind):
        return model.encode(texts, prompt_name=kind, normalize_embeddings=True)
    prefix = "query: " if kind == "query" else "passage: "
    return model.encode([prefix + t for t in texts], normalize_embeddings=True)


results = {}
for name in MODELS:
    model = SentenceTransformer(name)
    style = "config prompts" if has_prompt(model, "query") else "manual prefixes"
    print(f"{name}  ({style})")

    vectors = embed(model, raw_texts, "document")

    ranks = []
    for question, correct in GROUND_TRUTH:
        qv = embed(model, [question], "query")[0]
        order = np.argsort(-(vectors @ qv))
        ranks.append(int(np.where(order == correct)[0][0]) + 1)
    results[name] = ranks

print()
print("=" * 78)
print(f"{'question':<46}" + "".join(f"{m.split('/')[-1][:13]:>15}" for m in MODELS))
print("=" * 78)
for i, (question, _) in enumerate(GROUND_TRUTH):
    print(f"{question[:44]:<46}" + "".join(f"{'rank ' + str(results[m][i]):>15}" for m in MODELS))
print("=" * 78)
for m in MODELS:
    r = results[m]
    print(f"{m:<42} recall@1 {sum(x == 1 for x in r)}/{len(r)}   MRR {np.mean([1/x for x in r]):.3f}")
