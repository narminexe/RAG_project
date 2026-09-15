r"""
EVAL STEP 3 - The evaluation metrics for one eval run.

RETRIEVAL - did the bot read the right page? Only for questions whose answer is on the
bot's pages (in_documents = yes), using the source_pages column of the questions CSV.
"5" = the 5 chunks the answer model reads; several chunks can come from the same page.
  hit@5        share of answers where at least one right page was read
  recall@5     share of all right pages that were read
  precision@5  share of the pages read that were right pages
  MRR          1 / position of the first right page (1st = 1, 2nd = 0.5, ...), averaged

GENERATION - was the reply good? From the judge's grades in judged.jsonl.
  answer correctness   the judge said correct
  faithfulness         no made-up programme fact
  refusal accuracy     a proper "I don't know" when the answer is not on the pages (in_documents = no)

Run:  .venv\Scripts\python.exe spike\12_eval_metrics.py                   (newest eval run)
      .venv\Scripts\python.exe spike\12_eval_metrics.py results\eval\...  (a chosen run)
Output: metrics.json next to answers.jsonl
"""
import csv
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "eval" / "dp_eval_questions.csv"

_spec = importlib.util.spec_from_file_location("judge", ROOT / "spike" / "11_eval_judge.py")
judge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(judge)


def mean(values):
    return round(sum(values) / len(values), 2) if values else None


if len(sys.argv) > 1:
    folder = pathlib.Path(sys.argv[1]).resolve()
else:
    folder = sorted(p for p in (ROOT / "results" / "eval").glob("*") if (p / "judged.jsonl").exists())[-1]

rows = {row["question"].strip(): row
        for row in csv.DictReader(open(QUESTIONS, encoding="utf-8-sig", newline=""))}
records = [json.loads(line) for line in (folder / "answers.jsonl").read_text(encoding="utf-8").splitlines()]
for r in records:
    r["in_documents"] = rows[r["question"]]["in_documents"]
    r["right_pages"] = [p for p in rows[r["question"]].get("source_pages", "").split(";") if p]

# grades from the current judge, given under the label the CSV has now
by_key = {(r["id"], r["run"]): r for r in records}
grades = {}
for line in (folder / "judged.jsonl").read_text(encoding="utf-8").splitlines():
    g = json.loads(line)
    answer = by_key.get((g["id"], g["run"]))
    if answer and g.get("judge") == judge.JUDGE_TAG and g.get("in_documents") == answer["in_documents"]:
        grades[(g["id"], g["run"])] = g

hit, recall, precision, rr = [], [], [], []
for r in records:
    if r["in_documents"] != "yes" or not r["right_pages"]:
        continue
    read = r["pages"]                                   # in the order the bot ranked them
    found = [p for p in read if p in r["right_pages"]]
    hit.append(1 if found else 0)
    recall.append(len(found) / len(r["right_pages"]))
    precision.append(len(found) / len(read) if read else 0)
    rr.append(next((1 / n for n, p in enumerate(read, 1) if p in r["right_pages"]), 0))

graded = [r for r in records if (r["id"], r["run"]) in grades]
grade = lambda r: grades[(r["id"], r["run"])]
should_refuse = [r for r in graded if r["in_documents"] == "no"]

metrics = {
    "run": folder.name,
    "judge": judge.JUDGE_TAG,
    "retrieval (answers with a right page)": len(hit),
    "hit@5": mean(hit),
    "recall@5": mean(recall),
    "precision@5": mean(precision),
    "MRR": mean(rr),
    "generation (graded answers)": len(graded),
    "answer correctness": mean([grade(r)["grade"] == "correct" for r in graded]),
    "faithfulness": mean([not grade(r)["made_up"] for r in graded]),
    "refusal accuracy": mean([grade(r)["grade"] == "correct" for r in should_refuse]),
}
if len(graded) < len(records):
    print(f"note: only {len(graded)} of {len(records)} answers are graded by {judge.JUDGE_TAG}")

(folder / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
for name, value in metrics.items():
    print(f"{name:<40} {value}")
