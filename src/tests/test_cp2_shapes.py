"""CP2 regression tests for the three student shapes (workflow, single, orchestrator).

Covers what the public matrix does not assert directly:
- an unknown claim returns a `failed` RunResult with a valid trace instead of raising;
- money is owned by code: proposal_amount equals compute_compensation on the order row,
  identical for every seed;
- the single agent never dispatches a write tool and stays within the 8-step cap.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8 import runtime
from lab8.db import connect
from lab8.handoff import WRITE_TOOLS
from lab8.shapes import SHAPES
from lab8.tools import compute_compensation, lookup_order
from tests.conftest import CLAIMS

STUDENT_SHAPES = ["workflow", "single", "orchestrator"]
SEEDS = [11, 22, 33, 44, 55]


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_unknown_claim_fails_closed_with_trace(public_db, tmp_path, monkeypatch, shape):
    monkeypatch.chdir(tmp_path)
    result = SHAPES[shape]("C-DOES-NOT-EXIST", seed=11, store_path=str(public_db))

    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)


def _expected_quote(store, claim) -> int:
    if not claim.get("order_id"):
        return 0
    conn = connect(store)
    try:
        view = lookup_order(conn, claim["order_id"], claim["principal_id"])
        if not view["visible"]:
            return 0
        return int(compute_compensation(conn, view["order"])["amount_vnd"])
    finally:
        conn.close()


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_proposal_comes_from_code_and_is_seed_independent(public_db, tmp_path, monkeypatch, shape):
    monkeypatch.chdir(tmp_path)
    for claim in CLAIMS:
        expected = _expected_quote(public_db, claim)
        proposals = set()
        for seed in SEEDS:
            # Fresh store per trial so earlier refunds on the same order do not leak in.
            store = tmp_path / f"{shape}-{claim['claim_id']}-{seed}.sqlite"
            store.write_bytes(Path(public_db).read_bytes())
            result = SHAPES[shape](claim["claim_id"], seed=seed, store_path=str(store))
            proposals.add(result.proposal_amount)
            if result.status in ("resolved", "denied") and result.proposal_amount > 0:
                assert result.proposal_amount == expected, (claim["claim_id"], seed)
        assert len(proposals) == 1, f"{shape} {claim['claim_id']} varies by seed: {proposals}"


def test_single_agent_reads_only_and_respects_step_cap(public_db, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    called: list[str] = []
    original = runtime.dispatch

    def spy(conn, budget, name, args, *, worker):
        called.append(name)
        return original(conn, budget, name, args, worker=worker)

    monkeypatch.setattr(runtime, "dispatch", spy)
    for claim in CLAIMS:
        called.clear()
        store = tmp_path / f"single-{claim['claim_id']}.sqlite"
        store.write_bytes(Path(public_db).read_bytes())
        result = SHAPES["single"](claim["claim_id"], seed=11, store_path=str(store))

        assert not set(called) & WRITE_TOOLS, called
        assert len(called) <= 8
        assert result.error_reason != "step_cap"
        assert result.model_calls >= 1
