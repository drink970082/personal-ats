#!/usr/bin/env python3
"""Fold the reviewed answers back into `eval/golden.jsonl` — step 5 of the corpus rebuild.

`review_server.py` collects verdicts into `golden_review_answers.json` and nothing reads
them. This is that reader: it turns each answered row into a corpus row carrying an
inline `posting` payload, so the rebuilt corpus is self-contained and cannot decay the
way the last one did (22 of 93 rows name postings no longer in the DB, and
`score_eval.py` now FAILS on them rather than shrinking the gate around them).

WHAT COUNTS AS A LABEL, and the distinction is the point. Only ids the human actually
answered are written by default. Two-backend consensus is *not* a human label: a corpus
built from the scorer's own verdicts measures agreement, not correctness, so a genuinely
better challenger scores as a regression. `--consensus` folds those rows in anyway for
anyone who wants the larger set; they are stamped `label_source: "backend-consensus"` so
the two populations can never be confused after the fact.

Answers for ids outside this labelling run are ignored — the operator's earlier answers
were written while the profile and title filters were mid-edit, and the review shows them
as context that grades nothing.

    PYTHONPATH=. python3 tools/fold_review.py \\
        --codex eval/codex_labels_20260802.jsonl \\
        --claude eval/claude_code_labels_20260802.jsonl          # dry run, prints a plan
    PYTHONPATH=. python3 tools/fold_review.py ... --write        # writes golden.jsonl

Read-only on the DB. Dry-run by default; `--write` backs the old corpus up first.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/applications.db"
EVAL = ROOT / "apps/worker/eval"
# The same four columns `score_eval._cols_for` reads, in the same order. A payload that
# omits one is rejected by the eval's `all(c in inline for c in COLS)` presence check.
COLS = ("job_title", "company_name", "description", "location")
SENIORITY = {"match", "too_junior", "too_senior"}
DOMAIN = {"match", "adjacent", "mismatch"}


def read_labels(path: Path) -> dict:
    return {int(r["id"]): r
            for r in (json.loads(l) for l in path.read_text().splitlines() if l.strip())}


def band_for(seniority: str, domain: str) -> str:
    """The same derivation `label_golden.py` uses, so hand-labelled and folded rows sort
    into the same bands. Recomputed from the verdicts, never carried from the frame."""
    if seniority == "match" and domain == "match":
        return "keep"
    return "near" if domain == "adjacent" else "skip"


def plan_rows(answers: dict, run_ids: set, consensus: dict) -> tuple[list, dict]:
    """(rows_to_label, reasons) — pure, so the policy is testable without a DB.

    `rows_to_label` is (id, seniority, domain, note, source) for every row that should end
    up in the corpus. `reasons` counts what was dropped and why, because a fold that
    silently loses rows reads exactly like a fold that had nothing to lose.
    """
    out, dropped = [], {"rejected": [], "not_in_run": [], "incomplete": []}
    for key, ans in answers.items():
        rid = int(key)
        if rid not in run_ids:
            dropped["not_in_run"].append(rid)
            continue
        if ans.get("exclude") == "reject":
            dropped["rejected"].append(rid)
            continue
        sen, dom = ans.get("seniority"), ans.get("domain")
        # A half-answered row is a row the human started and did not finish. Writing it
        # with one verdict guessed is worse than leaving it out: the gate would score a
        # guess as ground truth.
        if sen not in SENIORITY or dom not in DOMAIN:
            dropped["incomplete"].append(rid)
            continue
        out.append((rid, sen, dom, ans.get("note") or "", "human-review"))

    answered = {int(k) for k in answers}
    for rid, row in sorted(consensus.items()):
        if rid in answered:
            continue     # a human answer overrides the machines' agreement
        out.append((rid, row["seniority"], row["domain"],
                    row.get("domain_note") or "", "backend-consensus"))
    out.sort(key=lambda t: t[0])
    return out, dropped


def payload_for(conn, rid: int, existing: dict) -> dict | None:
    """The posting to travel with the label. DB first (the live row is the fresher copy
    of the same posting, and ids are AUTOINCREMENT so they are never recycled); an
    existing inline payload second, which is what lets an already-self-contained row
    survive its posting leaving the DB."""
    got = conn.execute(
        f"SELECT {', '.join(COLS)} FROM job_postings WHERE id=?", (rid,)).fetchone()
    if got is not None:
        return dict(zip(COLS, got))
    prior = (existing.get(rid) or {}).get("posting")
    if isinstance(prior, dict) and all(c in prior for c in COLS):
        return prior
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--codex", type=Path, required=True)
    ap.add_argument("--claude", type=Path, required=True)
    ap.add_argument("--answers", type=Path, default=EVAL / "golden_review_answers.json")
    ap.add_argument("--out", type=Path, default=EVAL / "golden.jsonl")
    ap.add_argument("--consensus", action="store_true",
                    help="also fold rows both backends agreed on (machine labels)")
    ap.add_argument("--keep-unreachable", action="store_true",
                    help="keep a row whose posting is in neither the DB nor an inline "
                         "payload; it will FAIL the gate until relabelled")
    ap.add_argument("--write", action="store_true", help="write; otherwise dry-run")
    args = ap.parse_args()

    codex, claude = read_labels(args.codex), read_labels(args.claude)
    run_ids = set(codex) & set(claude)
    consensus = {}
    if args.consensus:
        consensus = {
            i: codex[i] for i in run_ids
            if not (codex[i].get("error") or claude[i].get("error"))
            and (codex[i].get("seniority"), codex[i].get("domain"))
            == (claude[i].get("seniority"), claude[i].get("domain"))}

    answers = json.loads(args.answers.read_text()) if args.answers.exists() else {}
    existing = {}
    if args.out.exists():
        existing = {r["id"]: r
                    for r in (json.loads(l) for l in args.out.read_text().splitlines()
                              if l.strip())}

    planned, dropped = plan_rows(answers, run_ids, consensus)

    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows, unreachable = [], []
    for rid, sen, dom, note, source in planned:
        posting = payload_for(conn, rid, existing)
        if posting is None:
            unreachable.append(rid)
            if not args.keep_unreachable:
                continue
        prior = existing.get(rid, {})
        row = {"id": rid, "band": band_for(sen, dom),
               # `hard` and `marked` are hand-set policy flags, not verdicts: `hard` makes
               # a wrong notify decision a gate VIOLATION, `marked` exempts a watch-list
               # row from the accuracy gate. A re-fold must not silently clear either.
               "hard": bool(prior.get("hard")),
               "note": note or prior.get("note", ""),
               "seniority": sen, "domain": dom, "label_source": source}
        if prior.get("marked"):
            row["marked"] = True
        if posting is not None:
            row["posting"] = posting
        rows.append(row)
    conn.close()

    human = sum(1 for r in rows if r["label_source"] == "human-review")
    gate_rows = [r for r in rows if not r.get("marked")]
    print(f"corpus: {len(rows)} rows ({human} human-reviewed, "
          f"{len(rows) - human} backend-consensus) · {len(gate_rows)} gate-eligible",
          file=sys.stderr)
    print(f"  dropped: {len(dropped['rejected'])} rejected, "
          f"{len(dropped['incomplete'])} half-answered, "
          f"{len(dropped['not_in_run'])} answers outside this run", file=sys.stderr)
    if unreachable:
        kept = "KEPT (they will fail the gate)" if args.keep_unreachable else "dropped"
        print(f"  {len(unreachable)} unreachable {kept}: "
              f"{', '.join(str(i) for i in unreachable[:12])}"
              f"{' ...' if len(unreachable) > 12 else ''}", file=sys.stderr)
    if dropped["incomplete"]:
        print(f"  half-answered ids (finish or drop them in the sheet): "
              f"{', '.join(str(i) for i in dropped['incomplete'])}", file=sys.stderr)

    if not args.write:
        print(f"\ndry run — nothing written. Re-run with --write to replace {args.out}",
              file=sys.stderr)
        return 0
    if not rows:
        print("refusing to write an empty corpus", file=sys.stderr)
        return 1
    if args.out.exists():
        backup = args.out.with_suffix(args.out.suffix + ".pre-fold")
        shutil.copy2(args.out, backup)
        print(f"backed up {args.out} -> {backup}", file=sys.stderr)
    args.out.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"wrote {len(rows)} rows -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
