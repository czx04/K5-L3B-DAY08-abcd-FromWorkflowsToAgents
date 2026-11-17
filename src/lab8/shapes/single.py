"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")

    # The agent sees the allowlisted claim view. Ticket text is data, not instructions.
    observation = {
        "claim": {
            "claim_id": claim_id,
            "principal_id": claim["principal_id"],
            "order_id": claim.get("order_id"),
            "ticket": claim.get("ticket", ""),
        }
    }
    memory: dict[str, Any] = {}
    steps: list[dict[str, Any]] = []

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        """One ReAct step. Picks read tools only; the amount always comes from compute_compensation."""
        if "last_tool" in seen:
            memory[seen["last_tool"]] = seen["last_result"]
        view = observation["claim"]
        prompt = view["ticket"] if not memory else f"seen={sorted(memory)}"
        complete(budget, seed=seed, purpose="react", prompt=prompt)

        action = _next_action(view, memory)
        steps.append({"action": action.get("tool") or "final", "status": (action.get("final") or {}).get("status")})
        return action

    loop = run_react(conn, budget, observation=observation, decide=decide, max_steps=MAX_STEPS)
    trace.add("react", {"stopped": loop["stopped"], "steps": steps})
    final = loop["final"]

    if loop["stopped"] == "step_cap":
        return done("failed", 0, "step_cap")
    if final["status"] in ("needs_info", "escalated", "failed"):
        return done(final["status"], 0, final.get("error_reason"))

    # Code, not the model, reads the quote produced by the deterministic tool.
    order_view = memory.get("lookup_order") or {}
    quote = memory.get("compute_compensation") or {}
    trace.add("order", safe_dump(order_view.get("order") or {}))
    trace.add("refund_history", safe_dump({k: memory.get("lookup_refund_history", {}).get(k) for k in ("refund_count", "refunded_vnd")}))
    trace.add("quote", safe_dump(quote))
    proposal = int(quote.get("amount_vnd") or 0)
    if proposal <= 0:
        return done("denied", 0, quote.get("reason") or "no_entitlement")

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)


def _next_action(view: dict[str, Any], memory: dict[str, Any]) -> dict[str, Any]:
    if not view.get("order_id"):
        return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
    scope = {"order_id": view["order_id"], "principal_id": view["principal_id"]}
    if "lookup_order" not in memory:
        return {"tool": "lookup_order", "args": scope}
    order_view = memory["lookup_order"]
    if not order_view.get("visible"):
        return {"final": {"status": "escalated", "error_reason": order_view.get("reason")}}
    if "lookup_refund_history" not in memory:
        return {"tool": "lookup_refund_history", "args": scope}
    if "compute_compensation" not in memory:
        # Structured order row only. Delay numbers in the ticket are ignored.
        return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
    return {"final": {"status": "propose"}}
