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

---

## D-005 — Generator LLM: gpt-4o-mini via OpenAI API (2026-09-09)

**Decision:** `gpt-4o-mini` writes the answers. `PROVIDER` in `spike/08_answer.py`
switches between OpenAI and a local Ollama model in one line.

**Options considered:** local Ollama (qwen3:4b, gemma3:4b), OpenAI API, Azerbaijani
fine-tunes (`az-llm/atllama`).

**Why this one:** local generation does not fit this laptop. 7.8 GB RAM with ~0.5 GB
free; `qwen3:4b` needs ~2.4 GB for weights alone and failed with
`failed to allocate CUDA_Host buffer`. Measured cost on the API is $0.000142 per
question, ~$0.0085 for a 60-question run, so a $4.50 credit is ~31,000 questions.
Not a constraint.

Azerbaijani fine-tunes rejected: `atllama.v3.5` ships no GGUF (16 GB safetensors,
would need self-quantising), has zero published evaluation, and an Alpaca-style
fine-tune on top of Llama-3.1-Instruct risks damaging instruction-following —
which is the thing RAG actually needs, more than fluency. Base Llama was rejected
because Meta does not list Azerbaijani among its 8 supported languages.

**What it costs:** the system is no longer fully local, which PLAN.md originally
wanted. Needs internet and a key per answer.

**What would change my mind:** more RAM, or a local model that measurably writes
acceptable Azerbaijani. Both stay open as Phase 4 experiment 7 — `qwen3:4b` is
already pulled.

---

## D-006 — General knowledge stays OFF for now (deferred, 2026-09-10)

**Decision:** The bot answers only from retrieved documents. It may NOT use its own
world knowledge, even for harmless general facts. Revisit after the project works
end to end.

**The case for changing it:** "6.5 IELTS bəsdir?" cannot be answered today. The site
states "minimum C1" and never mentions an IELTS number, so the CEFR↔IELTS mapping
is not in the corpus and the bot correctly refuses.

**Why not yet:** opening the door to outside knowledge also lets invented
programme-specific facts through — a plausible-sounding deadline or quota from
training data, stated as confidently as a true answer. People make real decisions on
this. It also makes faithfulness scores noisy, because a correct general claim is not
in the retrieved text and a judge marks it unfaithful.

**Preferred fix instead:** add a published CEFR↔IELTS mapping as its own corpus
document. Then the fact is IN the documents, the strict rule survives, and the answer
gets a citation. Less work than the testing that Option A would need.

**Revisit when:** `data/questions.csv` and the Phase 3 harness exist, so the change
can be measured rather than guessed at.

---

## D-005 (revised 2026-09-10) — Answer model: gpt-4.1-mini; search steps: gpt-4o-mini

Same test questions, same retrieved chunks, same answer rule — only the model changed:

| model | auto-checks | kept the no-outside-facts rule on "6.5 IELTS"? | $ per answer |
|---|---|---|---|
| gpt-4o-mini | 18/20 | no — "Bəli", then "you can't apply" | 0.00027 |
| gpt-4o | 20/20 | no — invented "7.0" | 0.00468 |
| **gpt-4.1-mini** | **20/20** | **yes** | **0.00077** |
| gpt-5-mini | 17/20 | yes, but messy | 0.00057 |

gpt-4o-mini failed on "burs" and "IELTS neçə bal" with the right text in front of it:
too literal. gpt-4.1-mini matched gpt-4o at a sixth of the price. gpt-4o-mini stays for
the two search-side steps (rewrite, pick), where it worked. Whole question: ~5 s,
~$0.0016. The Ollama switch is now `BASE_URL` in `spike/08_answer.py`.

The "kept the rule" column was measured under the old rule. D-006 (revised) now allows
that conversion when it is labelled.

---

## D-006 (revised 2026-09-10) — General knowledge: allowed for terms and scale conversions

**Supersedes** the D-006 above, which is kept for the record.

**Decision:** two kinds of information.
- **Programme facts** — rules, requirements, dates, amounts, documents, quotas,
  universities, obligations. Only from retrieved documents, never from the model's
  memory. If missing: "Bu məlumat sənədlərdə yoxdur".
- **General facts** — short explanations of terms that appear in the programme's rules
  ("IELTS nədir?") and standard international scale conversions ("6.5 IELTS C1-dir?").
  The model may answer these from its own knowledge in 1-2 sentences, always labelled
  "(ümumi məlumat, rəsmi sənəddən deyil)". No advice (exam preparation, choosing a
  university).

**Why:** real applicants ask these. A bot that refuses "IELTS nədir?", or cannot say
whether 6.5 meets C1, is not useful. I chose not to add a separate conversion table to
the corpus.

**What it costs:**
- Scale conversions decide eligibility, and published tables disagree at the edges.
  A labelled general answer can still steer a real decision.
- The line is fuzzy. "Magistratura üçün hansı sənədlər lazımdır?" sounds general but is
  a programme fact. This has to be tested on purpose, with questions built to cross it.
- Faithfulness metrics: a correct general claim is not in the retrieved text, so a judge
  marks it unfaithful. Evaluation must score labelled general parts separately.

**What would change my mind:** the bot stating a programme fact from memory in testing,
or finding an official conversion table on dp.edu.az (15 PDFs are still unindexed).

---

## D-007 — Search: 4 versions of the question, then the LLM picks the best 5 (2026-09-10)

**Problem:** people say "ortalama", "burs", "təqaüd", "diplom balı"; the site says "ÜOMG"
and "maliyyələşdirmə". One embedding search put the right text in the top 5 for only
13 of 19 casual questions.

**Tested on the same 19 questions** (right text in top 5 / MRR):

| approach | top 5 | MRR |
|---|---|---|
| one search (before) | 13/19 | 0.516 |
| LLM-written "likely questions" stored with each chunk | 12/19 | 0.411 |
| 4 versions of the question, results merged (RRF) | 16/19 | 0.715 |
| **+ LLM reads 25 candidates, picks 5** | **18/19** | **0.820** |

Storing likely questions per chunk was rejected: the LLM wrote formal, partly off-topic
questions ("ÜOMG nədir?") and never used words like "ortalama", so it added noise.

**Also fixed:** embedding the 300-character context prefix pushed IELTS answers from
rank 1-2 down to 6-7, because the prefix is mostly identical legal boilerplate. Chunks
are now searched on their clean text; the answer model still sees the prefixed version.

**What it costs:** two extra small LLM calls per question (~2-4 s, ~$0.0008).

**Known risk:** a rewrite once invented a number ("75 bal"). Harmless only because
rewrites are used for searching and never reach the user or the answer model.

**Still failing:** "Dövlət proqramına müraciət etmək üçün bakalavr ortalamam nə qədər
olmalıdır" — the question never says magistratura, so it is read as a bachelor's
question and answered with entrance-exam points. Needs the bot to ask back.

**Caveat:** 19 questions, written by me, one run each. A strong sign, not proof —
data/questions.csv is what turns it into a measurement.

---

## D-008 — Conversation layer: spike/09_chat.py (2026-09-10)

**Decision:** the chatbot wraps the RAG steps of 08_answer.py in a conversation layer.

1. **Understand** — one small JSON call (gpt-4o-mini) reads the new message plus the
   last 3 turns and labels it: chat (greeting, thanks, "who are you"), offtopic, or
   programme. Chat and offtopic get a short friendly reply with no search. A programme
   message gets a complete stand-alone question plus 3 search rewrites.
2. **Search + pick** — reused from 08_answer.py, so it lives in one place.
3. **Answer** — warm tone, "siz", simple words, 2-5 sentences. Programme facts only
   from the documents. If they are missing, the model writes the marker NO_ANSWER and
   the code swaps in a fixed friendly refusal with dp22-28@edu.gov.az. A fixed marker
   is easy to detect and count, and the email can never be mistyped.
4. A disclaimer opens every chat: unofficial student project, verify on dp.edu.az.

**The rule that must not break:** rewrites are for SEARCHING only. The answer model
reads the user's own message plus the conversation. The first version gave the answer
model the rewrite instead; the rewrite turned "ortalama" (GPA) into "ortalama xərclər"
(average costs), and a question 08 answered correctly 3 times out of 3 was answered
with a list of expenses.

**D-006 narrowed:** general knowledge only for international standards (IELTS, CEFR,
TOEFL, scale conversions). Terms specific to Azerbaijan or the programme (for example
ÜOMG) are explained only from the documents. Reason: the bot, labelled "ümumi məlumat",
claimed ÜOMG means high-school grades. That is false.

**Result on 13 scripted messages (after the fix):** greeting, thanks and offtopic
replies natural; "magistratura üçün ortalama" -> 81; the follow-up "bəs bakalavr
üçün?" -> entrance-exam points 400/550; "79 ortalamam var, bəsdir?" -> Xeyr, 81.
About 3 s and $0.0012 per message.

**Still wrong:**
- "pulsuz noutbuk verilirmi?" -> a confident "Xeyr", inferred from the list of funded
  expenses. The documents never mention laptops. It should say what the documents do
  cover and point to the email.
- a Russian question gets an Azerbaijani answer, despite the rule
- "bakalavr ortalamam..." answers only the bachelor case, not the master 81 case
- in one run an answer dropped an important condition that an earlier run included
- the bot says "Salam" again in the middle of a conversation
