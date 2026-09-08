# PLAN.md — Dövlət Proqramı RAG Chatbot

## Context for Claude Code

I am a Data Science student building a portfolio project. This is a RAG chatbot that answers questions about the Azerbaijani state study-abroad scholarship ("Xaricdə təhsil üzrə Dövlət Proqramı"), run by the Ministry of Science and Education.

The system runs entirely on my local machine.

**This project exists so I learn RAG deeply enough to defend every design choice in an interview.** A working repo I cannot explain is worthless to me.

---

## How I want you to work with me

This is the most important section. Follow it strictly.

### You write freely
- Scrapers, HTML/PDF extraction, file I/O
- Boilerplate, CLI scaffolding, logging, config loading
- Test fixtures and dev utilities
- Anything I have already implemented once and am now repeating

### You do NOT write until I have tried first
- Chunking logic
- Retrieval and ranking logic
- Evaluation metric implementations (recall@k, MRR, precision@k)
- Prompt templates
- Anything in the "core RAG" path

For these: ask me how I think it should work. Wait for my answer. Then correct my logic, fix my syntax, or tell me I'm wrong and why. If I say "just write it," push back once before complying.

### Stop and ask at every decision point
When there is a real choice to make — chunk size, which embedding model, k value, how to handle a contradiction in the corpus — do not pick for me. Present the options with tradeoffs and let me decide. Then record my decision and my reasoning in `DECISIONS.md`.

### Explain with my actual numbers
Do not explain concepts abstractly. Anchor everything to my corpus, my chunks, my scores. If recall@5 is 0.61, tell me what that means for these 150 questions specifically.

### Be direct
No filler, no praise, no "great question." If my approach is bad, say so and say why. If I'm about to waste a week, tell me on day one.

---

## Project constraints

- Python 3.11+, virtualenv, pinned dependencies from day one
- Git repo with meaningful commits at each phase boundary
- Everything reproducible: one command rebuilds the index, one command runs the eval
- Corpus language: Azerbaijani (with some Russian and English)
- Queries may arrive in Azerbaijani, Russian, or English

---

## Phase 0 — Question list and setup

**Goal:** a specification and a test set, before any pipeline exists.

### Step 0.1 — Build the question list

Before anything else, help me produce 60 questions a real applicant would ask.

Work interactively. Ask me what I already know about the program. Draft questions in batches of 10, I edit them, we move on. Cover these categories and label each question with its category:

| Category | Example shape |
|---|---|
| Eligibility | age limits, GPA, degree level requirements |
| Language requirements | IELTS/TOEFL minimums, exemptions |
| Deadlines | application dates, cycles |
| Funding scope | tuition, living costs, family members, insurance, visa |
| University/programme lists | which institutions, which specialisations, ranking criteria |
| Application process | portal, documents, stages, selection procedure |
| Obligations | return requirement, contract terms, repayment conditions |
| Quotas | total places, split across degree levels |
| Temporal traps | questions where the answer changed between years |
| Unanswerable | plausible questions the official documents do not answer |

Requirements:
- At least 15 in Azerbaijani, some in Russian, some in English
- At least 10 "temporal trap" questions
- At least 10 "unanswerable" questions — these test whether the bot refuses instead of inventing
- Mix of simple lookups and questions needing a number from a table

Store as `data/questions.csv` with columns:
`id, question, language, category, expected_answer, source_doc_ids, notes`

Leave `expected_answer` and `source_doc_ids` empty for now — they get filled after scraping.

**Explain to me, once, in two sentences, why this file is the project's test set and not busywork. Then move on.**

### Step 0.2 — Environment

Set up venv, requirements.txt, repo structure, .gitignore. Create empty `DECISIONS.md`. This is boilerplate — write it without asking me.

### Step 0.3 — Choose the generator LLM

Present me the options (Ollama local vs API) with the tradeoff for Azerbaijani quality. I decide. Record in DECISIONS.md.

---

## Phase 1 — Corpus

**Goal:** clean, versioned, metadata-rich documents on disk.

### Step 1.1 — Source inventory
Using my question list, work out which documents are needed. Search the relevant sites (dp.edu.az, edu.gov.az, the Cabinet of Ministers "Qayda" PDFs, yearly announcement pages) and produce `data/sources.csv`:
`doc_id, url, title, type, published_date, academic_year, language`

Show me the list. I approve before you scrape anything.

### Step 1.2 — Scraper
You write this. requests + BeautifulSoup, playwright only if needed. Rate limit to 1 req/sec, real User-Agent, respect robots.txt, cache raw HTML to `data/raw/` so we never re-scrape during development.

### Step 1.3 — PDF extraction
You write this. Use pymupdf. Flag any document where extraction looks broken (no text layer, interleaved columns, garbled diacritics). **Print samples and make me read them before we continue.** Bad extraction silently poisons everything downstream.

### Step 1.4 — Normalisation
Strip nav/footer/cookie banners. Handle Azerbaijani characters correctly — note that Python's default `.lower()` mishandles the dotted/dotless İ/ı. Flag this to me explicitly and show me a failing example.

Output: `data/processed/*.json`, one per document, text plus metadata.

### Step 1.5 — Fill in the test set
Now go back to `data/questions.csv`. For each question, I find the answer and the source doc_id(s) by hand. You help me search the corpus but **I make the final call on what counts as the correct answer.** Where no document answers it, mark it unanswerable.

---

## Phase 2 — Baseline RAG

**Goal:** a deliberately naive system to beat later. Do not optimise anything here.

### Step 2.1 — Chunking
Ask me first: what chunk size, what overlap, split on what boundary, why? I answer. You correct my reasoning, then help me implement it. Attach parent document metadata to every chunk.

### Step 2.2 — Embedding model
Present multilingual candidates suitable for Azerbaijani (multilingual-e5, bge-m3, paraphrase-multilingual-mpnet, others you find). I pick one for the baseline. We test the rest properly in Phase 4.

### Step 2.3 — Vector store
Chroma or FAISS locally. Verify I can do similarity search *and* metadata filtering in the same query — I need this for the academic-year problem.

### Step 2.4 — Retrieval function
Ask me to write the logic. Query in, top-k chunks out with source URLs.

**Then make me manually read the retrieved chunks for 10 questions before we add any generation.** No LLM yet. I need to see raw retrieval quality without fluency hiding it.

### Step 2.5 — Prompt template
I draft it. You critique. Must instruct: answer only from context, answer in the question's language, cite source URLs, refuse when the context doesn't contain the answer.

Then test the refusal behaviour against my unanswerable questions.

### Step 2.6 — Wire it together
Single `answer(question) -> (answer, sources)`. Ugly is fine. Commit as the baseline.

---

## Phase 3 — Evaluation harness

**This is the core of the project. Do not let me rush it.**

### Step 3.1 — Retrieval metrics
Ask me to define recall@k, precision@k, MRR in my own words first. Correct me. Then I implement, you fix syntax.

These need no LLM calls. They must run in seconds so I run them constantly.

Record baseline numbers in `results/baseline.json`.

### Step 3.2 — Generation metrics
Add RAGAS: faithfulness, answer relevancy, context precision, context recall. These cost LLM calls — run weekly on the full set, not on every change.

### Step 3.3 — Diagnostic output
The eval script must classify each failure:
- low context recall → chunking or retrieval problem
- high context recall + low faithfulness → prompt problem
- retrieved wrong academic year → metadata/filtering problem
- answered an unanswerable question → refusal problem

Print a summary table. A number I can't act on is useless.

### Step 3.4 — Regression suite
One command runs everything and writes a timestamped results file. Every subsequent change gets measured against it.

---

## Phase 4 — Ablations

For each experiment: change one variable, run the harness, record the result in `results/ablations.md` as a row in a table. Ask me to predict the outcome before we run it, then tell me if I was right.

1. **Chunking strategy** — 256 / 512 / 1024 chars, with and without overlap, vs paragraph-based, vs structural splitting on the legal documents' article numbering
2. **Embedding model** — the multilingual candidates, identical chunks. *This is the most novel result in the project: there is very little published on Azerbaijani retrieval quality.*
3. **Hybrid search** — add BM25, blend with dense scores. Consider lexical normalisation for an agglutinative language. Expect large gains on university names and exact figures.
4. **Reranking** — cross-encoder (bge-reranker-v2-m3) over top 30. Measure precision gain vs latency cost.
5. **Metadata filtering for academic year** — detect which year the query refers to, filter accordingly. Compare against no filtering.
6. **Cross-lingual retrieval** — non-Azerbaijani query against Azerbaijani documents. Compare translate-then-retrieve vs direct multilingual retrieval. *I have an NMT background; this is where it pays off.*
7. **Local vs API generator** — same retrieval, swap the model, measure the faithfulness delta honestly.

---

## Phase 5 — Ship

### Step 5.1 — Streamlit interface
Question box, answer, prominent source links, and a clear disclaimer: unofficial student project, verify against official sources. People make real decisions based on these rules — the disclaimer is an obligation, not a formality.

### Step 5.2 — Conversation memory
Rewrite follow-up questions ("bəs magistr üçün?") into standalone queries before retrieval.

### Step 5.3 — README
Architecture diagram, the ablation results table, the reasoning behind the final configuration, honest limitations, working setup instructions. The table is what a hiring manager reads.

### Step 5.4 — Demo GIF
Most people who open the repo will not clone it.

---

## Rules to hold me to

1. Do not let me skip Phase 0. The question list comes before code.
2. Do not let me skip Phase 3. A RAG demo without evaluation is not a portfolio project.
3. Do not let me start Phase 4 before the harness runs in one command.
4. If I ask you to "just write it" for anything in the core RAG path, push back once.
5. If I go off on a tangent, redirect me to the current step.
6. When I get discouraged, respond with what I have actually shipped so far, not encouragement.

## Start here

Begin with Phase 0, Step 0.1. Ask me what I already know about the Dövlət Proqramı, then draft the first 10 questions.
