# Dövlət Proqramı chatbot

A simple RAG chatbot for the State Programme of the Republic of Azerbaijan on education abroad.

**What is the programme?** The 2022-2028 State Programme pays for young Azerbaijanis to study at leading universities abroad at bachelor's, master's and doctoral level. It covers tuition, flights, visas and monthly living costs.

**Why this bot?** The programme's website, [dp.edu.az](https://dp.edu.az), has no chatbot. So students and parents, especially those applying for a bachelor's degree, often email the programme office with simple questions, or spend a long time looking around the website for one number. This bot answers those questions in Azerbaijani, using only the official pages and PDFs, and gives a link to the page it used. Later I plan to add official questions that programme staff have already answered, and information for students after they win the scholarship.

> This is an unofficial student project. Always check important details on dp.edu.az before making a decision.

## How it works

1. **Ingestion.** Downloads the pages and the key PDFs from dp.edu.az, turns them into clean text, and cuts the text into small chunks.
2. **Indexing.** Embeds each chunk with [`LocalDoc/LocRet-small`](https://huggingface.co/LocalDoc/LocRet-small), a model trained for Azerbaijani, and stores the vectors in Chroma.
3. **Understand.** An LLM reads the new message and the last few messages. It decides whether the message is small talk or a programme question, and rewrites short follow-ups ("bəs bakalavr üçün?") into full questions.
4. **Search and pick.** Searches with several versions of the question, then an LLM picks the 5 chunks that really answer it.
5. **Answer.** `gpt-4.1-mini` writes a short answer from those pages only. If they don't cover the question, the bot says so and gives the programme's contact email instead of guessing. `gpt-4.1-mini` is for this test demo; the real version will use Qwen.

A message takes about 3-5 seconds and costs about $0.002. Every design choice, with measurements, is in [DECISIONS.md](DECISIONS.md).

## Setup

You need Python 3.14 and an OpenAI API key. The commands below are for Windows and run from the project folder.

**1. Clone and install**

```bash
git clone https://github.com/narminexe/RAG_project.git
cd RAG_project
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**2. Add your API key**

Copy `.env.example` to `.env` and paste your key after `OPENAI_API_KEY=`. The `.env` file is gitignored.

**3. Build the search index**

The processed text is already in `data/processed/`, so you only need to build the index. The first run downloads the embedding model.

```bash
.venv\Scripts\python.exe spike\06_index_chroma.py
```

**4. Run the chatbot**

```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

It opens in your browser. The first message waits about 20 seconds while the model loads.

You can also chat in the terminal. Add `--debug` to see what the bot searched for and which pages it read:

```bash
.venv\Scripts\python.exe spike\09_chat.py --debug
```

## Refreshing the data

The website changes, for example when a new university list is published. To rebuild everything from dp.edu.az, run these in order:

```bash
.venv\Scripts\python.exe spike\00_download.py
.venv\Scripts\python.exe spike\01_extract.py
.venv\Scripts\python.exe spike\01b_list_status.py
.venv\Scripts\python.exe spike\01c_pdfs.py
.venv\Scripts\python.exe spike\02_chunk.py
.venv\Scripts\python.exe spike\06_index_chroma.py
```

`00_download.py` skips pages that are already saved in `data/raw/`. Delete that folder's contents to download everything again.

## Project structure

| Path | What it is |
|---|---|
| `app.py` | Streamlit web interface |
| `spike/00`-`06` | Ingestion: download, extract, chunk, index |
| `spike/08_answer.py` | Search, pick and answer for one question |
| `spike/09_chat.py` | The chatbot: conversation on top of `08_answer.py` |
| `scripts/discover_sources.py` | Finds the pages on dp.edu.az and writes `data/sources.csv` |
| `data/processed/` | Clean text and chunks |
| `DECISIONS.md` | Every design choice and why |

## Limitations

- The bot only knows what was on the website the last time the data was refreshed.
- It is built for Azerbaijani. Russian and English questions work, but less well.
- The monthly cost amounts come from a 2022 PDF on the website and may be out of date.
