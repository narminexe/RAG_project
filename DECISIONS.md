# DECISIONS.md

Every real choice in this project, with the reasoning behind it. Written so I can
defend each one. Four questions per entry: what else was on the table, why this,
what it cost me, what would make me change my mind.

---

## D-001 — Azerbaijani is the priority language (2026-09-09)

**Decision:** Optimise retrieval for Azerbaijani. Russian and English are supported
but never drive a decision.

**Why:** Roughly 97-98% of real questions to this chatbot will be in Azerbaijani.
I applied to this programme myself and so did many of my friends, so I know who
asks and how.

**What it costs:** Russian/English retrieval quality may be worse than if I had
optimised for all three equally.

**What would change my mind:** Evidence that non-Azerbaijani traffic is materially
higher than I think, or a model that is better at Azerbaijani *and* cross-lingual
at no extra cost.

**Consequence for the test set:** The PLAN.md split (~25% non-Azerbaijani out of 60
questions) over-weights 3% of real traffic. Instead: a **main set of ~50 Azerbaijani
questions** that drives every decision, plus a separate **cross-lingual guard set of
~10** Russian/English questions used only as a tripwire — checked, never averaged
into the headline metric, never optimised against.

---

## D-002 — Embedding model: LocalDoc/LocRet-small (2026-09-09)

**Decision:** Use `LocalDoc/LocRet-small` for chunk and query embeddings.

**Options considered:**

| Model | Params | AZ-MIRAGE MRR@10 | Note |
|---|---|---|---|
| **LocRet-small** | 118M | **0.5250** | Azerbaijani-specialised |
| bge-m3 | 568M | 0.4204 | 4.8x bigger, worse on AZ |
| multilingual-e5-large | 560M | 0.4043 | |
| multilingual-e5-small | 118M | 0.3586 | LocRet's base model |
| OpenAI text-embedding-3 | — | not benchmarked on AZ | paid, cannot pin version |

**Why this one:** Per D-001 my traffic is overwhelmingly Azerbaijani. LocRet is
fine-tuned from `multilingual-e5-small` on 3.5M Azerbaijani query-passage pairs
(listwise KL distillation from a bge-reranker-v2-m3 teacher). Same 118M parameters
and same 384 dimensions as the model it replaces, so the swap was one line and
costs nothing in speed or memory.

Unplanned second benefit found while switching: LocRet separates answerable from
unanswerable questions far better. An unrelated question ("Bakıda ən yaxşı kafe
hansıdır?") scores 0.02 against a real question's 0.32-0.49, where e5-small scored
that same junk question 0.78 against 0.87. A refusal threshold looks plausible with
LocRet and did not with e5. To be confirmed on the full test set.

**What it costs:** Fine-tuned on Azerbaijani only, so Russian/English retrieval may
degrade. Acceptable under D-001; the guard set exists to catch a collapse.

**Honest limitation:** AZ-MIRAGE is published by LocalDoc, the same team that
published the model. Not independent evidence. My own 60 questions are the
independent check, and I have not run that yet.

I did compare the two models directly on 4 questions (`spike/05_compare.py`):
e5-small MRR 0.875, LocRet 0.750. I am ignoring that result — 4 questions cannot
distinguish two models, they tied on 3 of them, and the one difference came down to
a ground-truth label I wrote myself and which was arguably wrong.

**What would change my mind:** LocRet losing to e5-small on the real 60-question set.
Switching back is one line.

---

## D-003 — Add a vector store (2026-09-09)

**Decision:** Yes. Chroma, added at the ingestion/indexing step.

**Why:** Right now every search re-embeds all chunks from scratch. At 10 chunks that
is 2 seconds; at 10,000 chunks it is minutes, on every single query. A vector store
embeds once, saves to disk, and reloads. It also gives metadata filtering, which I
need for the academic-year problem (filtering to the right tədris ili).

**What it costs:** One more dependency, and the index becomes a build artefact that
has to be rebuilt when chunking changes.

**What would change my mind:** Nothing at this scale — this is standard.

---

## D-004 — Work in the tutorial's order, not PLAN.md's (2026-09-09)

**Decision:** Follow the standard RAG pipeline order (ingestion -> chunking ->
embedding -> vector store -> retrieval -> generation), then return to PLAN.md's
evaluation phases.

**Why:** PLAN.md front-loads the 60-question test set before any working system
exists. That is correct for a portfolio project but I could not design a test set for
something I had never seen run. Seeing the pipeline work first makes the test set
concrete.

**What it costs:** The risk PLAN.md was guarding against — writing questions that
flatter a pipeline I have already seen. I mitigate this by writing questions from what
real applicants actually email, not from what I know the system handles.

**What would change my mind:** Nothing; the evaluation phases still happen, just later.
