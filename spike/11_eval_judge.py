r"""
EVAL STEP 2 - A stronger GPT model grades the answers saved by 10_eval_run.py and
writes the report.

For every saved answer, the judge reads:
  - the question and YOUR answer from the CSV
  - in_documents: yes = the bot's pages hold the answer, no = the bot should refuse
  - the bot's reply, and the conversation before it for a follow-up question
  - the text the bot read, so it can tell whether the bot made something up
It returns its reasoning FIRST and the grade LAST. Explaining before deciding makes the
judge more careful, and you can read why an answer failed.

Which judge: gpt-5.4, much stronger than the bot's gpt-4.1-mini. It is the same company as
the bot, and a judge can go easy on answers written like its own. That risk is small here,
because the judge compares the reply with YOUR answer under fixed rules instead of picking
a favourite, and the 20-answer check (your_grade in judged.csv) would show it.
Gemini was tried first and dropped on 2026-09-15: the free tier allowed about 20 grades a day.

Every grade is saved the moment it arrives, so if the script stops, run the same command
again and it carries on where it stopped.

Output, next to answers.jsonl:
  judged.jsonl   one grade per answer
  judged.csv     the same for Excel, with an empty your_grade column for the 20-answer check
  report.md      the scores and every failure with the judge's reason

Run:  .venv\Scripts\python.exe spike\11_eval_judge.py                   (newest eval run)
      .venv\Scripts\python.exe spike\11_eval_judge.py results\eval\...  (a chosen run)
"""
import csv
import hashlib
import json
import os
import pathlib
import sys
import time
from collections import Counter, defaultdict
from typing import Literal

from dotenv import load_dotenv
from openai import APIConnectionError, InternalServerError, OpenAI, RateLimitError
from pydantic import BaseModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "eval" / "dp_eval_questions.csv"
load_dotenv(ROOT / ".env")

JUDGE_MODEL = "gpt-5.4"
PRICE = (2.50, 15.00)              # $ per 1M tokens (input, output). Check the pricing page - these move.
WAIT = 20                          # seconds; the wait grows with each failed try
TRIES = 5
GRADES = ("correct", "partly", "wrong")


class Grade(BaseModel):
    reasoning: str                 # first on purpose: the judge explains, then decides
    grade: Literal["correct", "partly", "wrong"]
    made_up: bool


JUDGE_PROMPT = """You grade replies from a chatbot about Azerbaijan's State Programme for studying abroad (dp.edu.az). The questions come from real applicants, often in Azerbaijani typed without special letters.

THE BOT'S RULES
- Programme facts (requirements, dates, amounts, documents, quotas, lists, obligations) may come ONLY from the TEXT THE BOT READ.
- It may add a short explanation of international standards (IELTS, CEFR, ...) if it labels it "(ümumi məlumat, rəsmi sənəddən deyil)".
- It gives no advice.
- If the text does not answer the question, it refuses and gives the email dp22-28@edu.gov.az. If the message has nothing to do with the programme, it politely declines.

HOW TO GRADE. IN_DOCUMENTS = {in_documents}
Look at IN_DOCUMENTS first. It decides what a good reply is.
IN_DOCUMENTS was set by a human expert who checked the bot's documents. It is final: never decide it yourself, and never guess it from the reference answer. A detailed reference answer does NOT mean the bot's documents contain it.

If IN_DOCUMENTS is no: the programme's documents do not answer this question, so the bot is expected to decline. The reference answer, if any, is background only.
  correct = the bot refuses, says it has no information on this, or politely declines. Mentioning a few related facts is fine if it still says clearly that the exact answer is not available.
  partly  = it declines, but also states programme facts that the text does not support.
  wrong   = it gives an answer or advice as if it knew, even when every sentence comes from the text.

If IN_DOCUMENTS is yes: the answer exists in the programme's documents. Compare the BOT REPLY with the REFERENCE ANSWER.
  correct = the key facts match and nothing important is wrong or misleading.
  partly  = some key facts are right, but something important is missing or misleading (for example it starts with "No" when the facts mean "yes, in the end").
  wrong   = the key facts are wrong or missing. A refusal is ALWAYS wrong here, even if the TEXT THE BOT READ lacks the answer: that means the bot's search failed.
  Detail in the reference answer beyond its key facts is not required.

made_up = true if the reply states any programme fact that the TEXT THE BOT READ does not support, or applies a rule from the text to a different group than the text does (for example a rule for doctoral candidates presented as a rule for everyone). Labelled general knowledge, the refusal message and the contact email do not count.

The reply language does not change the grade; it is checked separately.
Write the reasoning first, in 2-4 sentences of English, then the grade.

CONVERSATION BEFORE THIS QUESTION:
{conversation}

QUESTION: {question}
REFERENCE ANSWER: {expected}
BOT REPLY: {reply}

TEXT THE BOT READ:
{context}"""

# Saved with every grade. A new model or any edit to the prompt gives a new tag, so old
# grades are ignored and everything is graded again the new way.
JUDGE_TAG = f"{JUDGE_MODEL} / prompt {hashlib.md5(JUDGE_PROMPT.encode()).hexdigest()[:6]}"


def ask_judge(client, prompt):
    """One grade. Returns (Grade, [input tokens, output tokens])."""
    for attempt in range(1, TRIES + 1):
        try:
            r = client.chat.completions.parse(
                model=JUDGE_MODEL, response_format=Grade,
                messages=[{"role": "user", "content": prompt}])
            grade = r.choices[0].message.parsed
            if grade:
                return grade, [r.usage.prompt_tokens, r.usage.completion_tokens]
        except RateLimitError as e:
            if e.code == "insufficient_quota":
                sys.exit("The OpenAI account is out of credit. Every grade so far is saved: "
                         "add credit, then run the same command again.")
            if attempt == TRIES:
                raise
        except (APIConnectionError, InternalServerError):
            if attempt == TRIES:
                raise
        if attempt == TRIES:
            sys.exit("The judge gave no usable grade after several tries.")
        print(f"      no grade this time, waiting {WAIT * attempt} s and trying again...")
        time.sleep(WAIT * attempt)


def write_report(folder, meta, records, grades):
    key = lambda r: (r["id"], r["run"])
    graded = [r for r in records if key(r) in grades]
    by_question = defaultdict(list)
    for r in graded:
        by_question[r["id"]].append(r)

    lines = [f"# Eval report: {folder.name}", "",
             f"Bot: answer model `{meta['answer_model']}`, search model `{meta['search_model']}`, "
             f"check model `{meta.get('check_model')}`, "
             f"read big = {meta['read_big']}. Judge: `{JUDGE_TAG}`.  ",
             f"{meta['questions']} questions x {meta['runs']} runs = {len(records)} answers."]
    if len(graded) < len(records):
        lines.append(f"\n**Only {len(graded)} of {len(records)} answers are graded so far.**")

    lines += ["", "## Scores (judge)", "", "| | correct | partly | wrong |", "|---|---|---|---|"]
    for label, group in (("should answer (in_documents = yes)", "yes"),
                         ("should refuse (in_documents = no)", "no"), ("all", None)):
        rs = [r for r in graded if group in (None, r["in_documents"])]
        counts = Counter(grades[key(r)]["grade"] for r in rs)
        cells = [f"{counts[g]} ({counts[g] / len(rs):.0%})" if rs else "-" for g in GRADES]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    as_expected = sum((r["in_documents"] == "no") == r["declined"] for r in records)
    wrong_lang = sorted({f"{r['id']} ({r['question_lang']} -> {r['reply_lang']})"
                         for r in records if r["question_lang"] != r["reply_lang"]})
    made_up = sorted({r["id"] for r in graded if grades[key(r)]["made_up"]})
    unstable = [q for q, rs in by_question.items() if len({grades[key(r)]["grade"] for r in rs}) > 1]
    judge_in = sum(g["tokens"][0] for g in grades.values())
    judge_out = sum(g["tokens"][1] for g in grades.values())
    lines += ["", "## Simple checks", "",
              f"- answers that answered or declined as expected (no LLM): {as_expected}/{len(records)}",
              f"- questions answered in another language (no LLM): {len(wrong_lang)}  {', '.join(wrong_lang)}",
              f"- questions with a made-up programme fact (judge): {len(made_up)}  {', '.join(made_up)}",
              f"- questions graded differently in different runs: {len(unstable)}  {', '.join(unstable)}",
              f"- bot errors: {sum(bool(r['error']) for r in records)}",
              f"- bot cost: ${sum(r['cost'] for r in records):.3f}, "
              f"{sum(r['seconds'] for r in records) / max(len(records), 1):.1f} s per answer",
              f"- judge cost: ${judge_in / 1e6 * PRICE[0] + judge_out / 1e6 * PRICE[1]:.3f}"]

    suspects = sorted({r["id"] for r in graded if r["in_documents"] == "no"
                       and not r["declined"] and not grades[key(r)]["made_up"]})
    if suspects:
        lines += ["", "## Check the label", "",
                  "in_documents = no, but the bot answered and the judge found every fact in the "
                  f"text it read. Maybe a page does answer these: {', '.join(suspects)}"]

    lines += ["", "## Failures", "", "Every question with at least one answer that is not correct. "
              "All runs are shown, so you can see when a question flips."]
    for qid, rs in by_question.items():
        if all(grades[key(r)]["grade"] == "correct" for r in rs):
            continue
        lines += ["", f"### {qid}: {rs[0]['question']}", "",
                  f"- in_documents: {rs[0]['in_documents']}",
                  f"- your answer: {rs[0]['expected']}"]
        for r in rs:
            g = grades[key(r)]
            reply = " ".join(r["reply"].split())
            lines += [f"- **run {r['run']}: {g['grade']}**{' (made up)' if g['made_up'] else ''}",
                      f"  - bot: {reply[:400]}{'...' if len(reply) > 400 else ''}",
                      f"  - judge: {g['reasoning']}",
                      f"  - pages read: {', '.join(r['pages']) or 'none'}"]

    (folder / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with open(folder / "judged.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "run", "question", "in_documents", "your_answer", "bot_reply",
                    "judge_grade", "made_up", "judge_reasoning", "your_grade"])
        for r in graded:
            g = grades[key(r)]
            w.writerow([r["id"], r["run"], r["question"], r["in_documents"], r["expected"],
                        r["reply"], g["grade"], g["made_up"], g["reasoning"], ""])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = pathlib.Path(sys.argv[1]).resolve()
    else:
        runs = sorted(p for p in (ROOT / "results" / "eval").glob("*") if (p / "answers.jsonl").exists())
        if not runs:
            sys.exit("No eval run found. Run spike\\10_eval_run.py first.")
        folder = runs[-1]
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("No OPENAI_API_KEY in .env - add it, then re-run.")

    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in
               (folder / "answers.jsonl").read_text(encoding="utf-8").splitlines()]
    # Labels are read from the CSV, not from answers.jsonl, so a label fixed after the
    # bot ran counts without asking the bot again.
    labels = {row["question"].strip(): row["in_documents"].strip().lower()
              for row in csv.DictReader(open(QUESTIONS, encoding="utf-8-sig", newline=""))}
    for r in records:
        r["in_documents"] = labels.get(r["question"], r["in_documents"])
    by_key = {(r["id"], r["run"]): r for r in records}

    judged_path = folder / "judged.jsonl"
    grades = {}
    if judged_path.exists():
        for line in judged_path.read_text(encoding="utf-8").splitlines():
            g = json.loads(line)
            answer = by_key.get((g["id"], g["run"]))
            # reuse a grade only if the same judge gave it under the same label
            if answer and g.get("judge") == JUDGE_TAG and g.get("in_documents") == answer["in_documents"]:
                grades[(g["id"], g["run"])] = g

    todo = [r for r in records if (r["id"], r["run"]) not in grades]
    print(f"{folder.name}: {len(records)} answers, {len(grades)} already graded, "
          f"{len(todo)} to grade with {JUDGE_TAG}", flush=True)

    client = OpenAI()
    try:
        with open(judged_path, "a", encoding="utf-8") as out:
            for n, r in enumerate(todo, 1):
                earlier = by_key.get((r["follow_up_of"], r["run"]))
                prompt = JUDGE_PROMPT.format(
                    in_documents=r["in_documents"],
                    conversation=f"User: {earlier['question']}\nBot: {earlier['reply']}" if earlier else "(none)",
                    question=r["question"],
                    expected=r["expected"] or "(none)",
                    reply=r["reply"] or "(empty: the bot crashed)",
                    context=r["context"] or "(nothing: the bot treated the message as small talk and did not search)")
                g, tokens = ask_judge(client, prompt)
                grades[(r["id"], r["run"])] = saved = {"id": r["id"], "run": r["run"], "judge": JUDGE_TAG,
                                                       "in_documents": r["in_documents"],
                                                       **g.model_dump(), "tokens": tokens}
                out.write(json.dumps(saved, ensure_ascii=False) + "\n")
                out.flush()
                print(f"{n:>3}/{len(todo)}  {r['id']} run {r['run']}  {g.grade:<7}"
                      f"{'  made up' if g.made_up else ''}  {r['question'][:50]}", flush=True)
    finally:                          # write the report even if the run stopped early
        write_report(folder, meta, records, grades)
        print(f"\nreport: {(folder / 'report.md').relative_to(ROOT)}")
