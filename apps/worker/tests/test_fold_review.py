"""Tests for tools/fold_review.py — folding reviewed answers back into `golden.jsonl`.

No DB and no network: `plan_rows`, `band_for` and `payload_for` carry the decisions, and
`payload_for` takes the connection as an argument so a fake covers it. The one thing
these must not do is open the operator's real `db/applications.db`.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "fold_review.py"
_spec = importlib.util.spec_from_file_location("fold_review", TOOL)
fold = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fold)

RUN = {1, 2, 3, 4, 5}


def test_band_is_recomputed_from_the_verdicts():
    assert fold.band_for("match", "match") == "keep"
    assert fold.band_for("match", "adjacent") == "near"
    assert fold.band_for("too_junior", "adjacent") == "near"
    assert fold.band_for("match", "mismatch") == "skip"
    assert fold.band_for("too_junior", "match") == "skip"


def test_only_answers_from_this_run_are_folded():
    """The operator's earlier answers were written mid-edit against a profile that has
    since changed; the review shows them as context that grades nothing, so an answer for
    an id outside the run must not become a label."""
    answers = {"1": {"seniority": "match", "domain": "match"},
               "999": {"seniority": "match", "domain": "match"}}
    rows, dropped = fold.plan_rows(answers, RUN, {})
    assert [r[0] for r in rows] == [1]
    assert dropped["not_in_run"] == [999]


def test_a_rejected_row_leaves_the_corpus():
    answers = {"1": {"exclude": "reject"}, "2": {"seniority": "match", "domain": "match"}}
    rows, dropped = fold.plan_rows(answers, RUN, {})
    assert [r[0] for r in rows] == [2]
    assert dropped["rejected"] == [1]


def test_a_half_answered_row_is_not_guessed():
    """One verdict set and the other blank is a row the human started and did not finish.
    Writing it would score a guess as ground truth."""
    answers = {"1": {"seniority": "match"}, "2": {"domain": "match"},
               "3": {"seniority": "match", "domain": "match"}}
    rows, dropped = fold.plan_rows(answers, RUN, {})
    assert [r[0] for r in rows] == [3]
    assert dropped["incomplete"] == [1, 2]


def test_a_bogus_verdict_string_is_rejected_not_written():
    answers = {"1": {"seniority": "match", "domain": "MATCH"},
               "2": {"seniority": "yes", "domain": "match"}}
    rows, dropped = fold.plan_rows(answers, RUN, {})
    assert rows == []
    assert sorted(dropped["incomplete"]) == [1, 2]


def test_consensus_is_stamped_and_never_overrides_a_human_answer():
    """Consensus is a machine label — a corpus built from the scorer's own verdicts
    measures agreement, not correctness — so it must be distinguishable afterwards, and
    a human answer on the same id must win."""
    consensus = {1: {"seniority": "match", "domain": "mismatch"},
                 2: {"seniority": "match", "domain": "match"}}
    answers = {"1": {"seniority": "too_junior", "domain": "adjacent"}}
    rows, _ = fold.plan_rows(answers, RUN, consensus)
    by_id = {r[0]: r for r in rows}
    assert by_id[1][1:3] == ("too_junior", "adjacent")
    assert by_id[1][4] == "human-review"
    assert by_id[2][4] == "backend-consensus"


def test_consensus_is_opt_in():
    rows, _ = fold.plan_rows({}, RUN, {})
    assert rows == []


class _FakeConn:
    """Stands in for sqlite3 so no test can reach the operator's DB."""

    def __init__(self, live: dict):
        self.live = live

    def execute(self, _sql, params):
        class _Cur:
            def __init__(self, row):
                self.row = row

            def fetchone(self):
                return self.row
        return _Cur(self.live.get(params[0]))


def _posting(**kw):
    return {c: kw.get(c, f"x-{c}") for c in fold.COLS}


def test_payload_prefers_the_live_db_row_over_a_stale_inline_copy():
    conn = _FakeConn({7: tuple(_posting(job_title="fresh")[c] for c in fold.COLS)})
    existing = {7: {"posting": _posting(job_title="stale")}}
    assert fold.payload_for(conn, 7, existing)["job_title"] == "fresh"


def test_payload_falls_back_to_an_existing_inline_copy():
    """This is the whole point of the inline payload: a row already carrying one survives
    its posting leaving the DB, which is how the previous corpus rotted to one row."""
    existing = {7: {"posting": _posting(job_title="carried")}}
    assert fold.payload_for(_FakeConn({}), 7, existing)["job_title"] == "carried"


def test_an_inline_copy_missing_a_column_is_not_usable():
    """`score_eval._cols_for` requires all four keys present; a partial payload would be
    accepted here and then silently skipped by the eval."""
    partial = _posting()
    del partial["location"]
    assert fold.payload_for(_FakeConn({}), 7, {7: {"posting": partial}}) is None


def test_unreachable_when_neither_source_has_it():
    assert fold.payload_for(_FakeConn({}), 7, {}) is None
