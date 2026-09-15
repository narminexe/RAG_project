r"""
EVAL STEP 1 - Ask the bot every test question and make a grading sheet.

Reads data/eval/dp_eval_questions.csv (question, answer, in_documents, source_pages) and
sends each question to chat() in 09_chat.py. That is the same function the Streamlit app
calls, so this measures the real bot, not a copy of it.

A question that starts with "bəs " ("and what about...") continues the conversation of
the question above it, the way a real user would ask it. Asked alone it makes no sense.

The replies are graded BY HAND. The set is small (up to ~100 questions), and the person who
knows the programme grades better: an LLM judge tried on 2026-09-15 matched the hand grades
on only 14 of 20 replies.

Output: results/eval/<date_time>/answers.jsonl   everything the bot did, one line per reply
        results/eval/<date_time>/grades.csv      the sheet you fill in
        results/eval/<date_time>/meta.json       which models and settings were tested

In grades.csv, fill in for every row:
  grade     correct, partly or wrong
  made_up   yes, if the reply states a programme fact that is not on the pages it read
  reason    optional: why
Save it in Excel as "CSV UTF-8", then run step 2.

Run:  .venv\Scripts\python.exe spike\10_eval_run.py
Next: .venv\Scripts\python.exe spike\11_eval_metrics.py
"""
import csv
import importlib.util
import json
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "eval" / "dp_eval_questions.csv"
RUNS = 1                              # 2 shows replies that change from run to run, but doubles the grading

# "import 09_chat" is not valid Python (a name cannot start with a digit), so load by path
_spec = importlib.util.spec_from_file_location("bot", ROOT / "spike" / "09_chat.py")
bot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bot)

EN_WORDS = {"a", "an", "the", "is", "are", "am", "do", "does", "did", "i", "my", "me", "you",
            "your", "what", "when", "where", "which", "who", "how", "can", "could", "will",
            "if", "on", "in", "of", "to", "for", "per", "while", "and", "or", "with", "this",
            "that", "it", "be", "get", "there", "yes", "not"}


def language(text):
    """A rough guess: "ru", "en" or "az".
    Many test questions are Azerbaijani typed without ə, ş, ğ ("neleri qarsilayir?"), so the
    letters alone cannot tell them apart from English. Common English words can."""
    words = re.findall(r"[^\W\d_]+", text.lower())
    if not words:
        return "az"
    if sum(bool(re.search("[а-яё]", w)) for w in words) > len(words) / 2:
        return "ru"
    if sum(w in EN_WORDS for w in words) >= max(2, len(words) // 5):
        return "en"
    return "az"


rows = list(csv.DictReader(open(QUESTIONS, encoding="utf-8-sig", newline="")))
out_dir = ROOT / "results" / "eval" / time.strftime("%Y-%m-%d_%H%M%S")
out_dir.mkdir(parents=True)

(out_dir / "meta.json").write_text(json.dumps({
    "date": time.strftime("%Y-%m-%d %H:%M"),
    "questions": len(rows),
    "runs": RUNS,
    "answer_model": bot.rag.ANSWER_MODEL,
    "check_model": bot.CHECK_MODEL if getattr(bot, "CHECK", False) else None,
    "search_model": bot.rag.SEARCH_MODEL,
    "base_url": bot.rag.BASE_URL,
    "read_big": bot.READ_BIG,
}, indent=2), encoding="utf-8")

print(f"{len(rows)} questions x {RUNS} run(s). Loading the bot (~20 s)...")
bot.rag._setup()

t0 = time.time()
records = []
with open(out_dir / "answers.jsonl", "w", encoding="utf-8") as out:
    for run in range(1, RUNS + 1):
        history, previous_id = [], None
        for n, row in enumerate(rows, 1):
            qid = f"q{n:02d}"
            question = row["question"].strip()
            follow_up = previous_id is not None and question.lower().startswith("bəs ")
            if not follow_up:
                history = []              # a new question starts a new conversation

            try:
                reply, info = bot.chat(question, history)
            except Exception as e:        # one failed call should not end the whole run
                reply, info = "", {"type": "error", "error": str(e)}

            record = {
                "id": qid,
                "run": run,
                "question": question,
                "expected": row["answer"].strip(),
                "in_documents": row["in_documents"].strip().lower(),
                "follow_up_of": previous_id if follow_up else None,
                "reply": reply,
                "type": info["type"],
                "declined": info["type"] in ("chat", "offtopic") or bool(info.get("refused")),
                "question_lang": language(question),
                "reply_lang": language(reply),
                "pages": list(dict.fromkeys(doc_id for _, doc_id in info.get("chosen", []))),
                "context": info.get("context", ""),
                "unsupported": info.get("unsupported"),   # what the check step found, if it ran
                "seconds": round(info.get("seconds", 0), 1),
                "cost": info.get("cost", 0),
                "error": info.get("error"),
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()                   # saved now, so a crash later loses nothing
            records.append(record)
            previous_id = qid

            as_expected = (record["in_documents"] == "no") == record["declined"]
            print(f"run {run}  {qid}  {'declined' if record['declined'] else 'answered':<8}  "
                  f"{'ok   ' if as_expected else 'CHECK'}  {question[:55]}")

with open(out_dir / "grades.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "run", "in_documents", "question", "correct_answer", "bot_reply",
                "pages_read", "grade", "made_up", "reason"])
    for r in records:
        w.writerow([r["id"], r["run"], r["in_documents"], r["question"], r["expected"],
                    r["reply"], ", ".join(r["pages"]), "", "", ""])

ok = sum((r["in_documents"] == "no") == r["declined"] for r in records)
lang = sum(r["question_lang"] != r["reply_lang"] for r in records)
print(f"\nanswered or declined as expected: {ok}/{len(records)}")
print(f"replied in another language:      {lang}")
print(f"errors:                           {sum(bool(r['error']) for r in records)}")
print(f"cost ~${sum(r['cost'] for r in records):.3f}, {time.time() - t0:.0f} s")
print(f"grade the replies in {(out_dir / 'grades.csv').relative_to(ROOT)}")
