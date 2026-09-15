r"""
EVAL STEP 2 - The evaluation metrics for one eval run.

RETRIEVAL - did the bot read the right page? Only for questions whose answer is on the
bot's pages (in_documents = yes), using the source_pages column of the questions CSV.
No grading needed. "5" = the 5 chunks the answer model reads; several can come from one page.
  hit@5        share of replies where at least one right page was read
  recall@5     share of all right pages that were read
  precision@5  share of the pages read that were right pages
  MRR          1 / position of the first right page (1st = 1, 2nd = 0.5, ...), averaged

GENERATION - was the reply good? From YOUR grades in grades.csv.
  answer correctness   grade is correct
  faithfulness         made_up is not yes
  refusal accuracy     grade is correct, on questions whose answer is not on the pages (in_documents = no)
Only graded rows count, so the numbers can be checked while grading is still going on.

Run:  .venv\Scripts\python.exe spike\11_eval_metrics.py                   (newest eval run)
      .venv\Scripts\python.exe spike\11_eval_metrics.py results\eval\...  (a chosen run)
Output: metrics.json next to answers.jsonl
"""
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "eval" / "dp_eval_questions.csv"
GRADES = ("correct", "partly", "wrong")


def mean(values):
    return round(sum(values) / len(values), 2) if values else None


if len(sys.argv) > 1:
    folder = pathlib.Path(sys.argv[1]).resolve()
else:
    folder = sorted(p for p in (ROOT / "results" / "eval").glob("*") if (p / "answers.jsonl").exists())[-1]

rows = {row["question"].strip(): row
        for row in csv.DictReader(open(QUESTIONS, encoding="utf-8-sig", newline=""))}
records = [json.loads(line) for line in (folder / "answers.jsonl").read_text(encoding="utf-8").splitlines()]
for r in records:
    r["in_documents"] = rows[r["question"]]["in_documents"]
    r["right_pages"] = [p for p in rows[r["question"]].get("source_pages", "").split(";") if p]

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

sheet = {}
if (folder / "grades.csv").exists():
    for row in csv.DictReader(open(folder / "grades.csv", encoding="utf-8-sig", newline="")):
        if row.get("id") and row.get("grade", "").strip().lower() in GRADES:   # Excel adds empty rows
            sheet[(row["id"], int(row["run"]))] = row
graded = [r for r in records if (r["id"], r["run"]) in sheet]
grade = lambda r: sheet[(r["id"], r["run"])]["grade"].strip().lower()
made_up = lambda r: sheet[(r["id"], r["run"])].get("made_up", "").strip().lower() == "yes"

metrics = {
    "run": folder.name,
    "retrieval (replies with a right page)": len(hit),
    "hit@5": mean(hit),
    "recall@5": mean(recall),
    "precision@5": mean(precision),
    "MRR": mean(rr),
    "generation (graded replies)": f"{len(graded)} of {len(records)}",
    "answer correctness": mean([grade(r) == "correct" for r in graded]),
    "faithfulness": mean([not made_up(r) for r in graded]),
    "refusal accuracy": mean([grade(r) == "correct" for r in graded if r["in_documents"] == "no"]),
}

(folder / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
for name, value in metrics.items():
    print(f"{name:<40} {value}")
