import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.handoff import HandoffError, make_handoff
from lab8.runtime import ToolRejected, dispatch
from lab8.schemas import Budget
from lab8.shapes import SHAPES
from lab8.shapes import orchestrator


SHAPES_UNDER_TEST = ['workflow', 'single', 'orchestrator']


def state(store):
    conn = connect(store)
    try:
        ledger = [dict(row) for row in conn.execute(
            "SELECT idempotency_key, amount_vnd, status FROM refund_ledger WHERE claim_id = 'C-001'"
        )]
        audits = [dict(row) for row in conn.execute(
            "SELECT audit_key, event_type FROM audit_events WHERE claim_id = 'C-001' ORDER BY audit_key"
        )]
        checkpoints = [json.loads(row['result_json']) for row in conn.execute(
            "SELECT result_json FROM checkpoints WHERE claim_id = 'C-001' AND step = 'issue_refund'"
        )]
        return ledger, audits, checkpoints
    finally:
        conn.close()


@pytest.mark.parametrize('shape', SHAPES_UNDER_TEST)
@pytest.mark.parametrize('point,expected_ledger,expected_checkpoint', [
    ('before_effect', 0, 0),
    ('after_effect_before_checkpoint', 1, 0),
    ('after_checkpoint', 1, 1),
])
def test_crash_and_resume_preserve_ledger_audit_and_checkpoint(public_db, tmp_path, monkeypatch, shape, point, expected_ledger, expected_checkpoint):
    monkeypatch.chdir(tmp_path)
    run = SHAPES[shape]
    with pytest.raises(InjectedCrash, match=point):
        run('C-001', seed=11, store_path=str(public_db), crash_at=point)
    ledger, audits, checkpoints = state(public_db)
    assert len(ledger) == expected_ledger
    assert len(audits) == expected_ledger
    assert len(checkpoints) == expected_checkpoint
    result = run('C-001', seed=11, store_path=str(public_db))
    replay = run('C-001', seed=11, store_path=str(public_db))
    assert result.status == replay.status == 'resolved'
    ledger, audits, checkpoints = state(public_db)
    assert ledger == [{'idempotency_key': 'refund:C-001', 'amount_vnd': 35000, 'status': 'committed'}]
    assert audits == [{'audit_key': 'refund_committed:C-001', 'event_type': 'refund_committed'}]
    assert checkpoints == [{'claim_id': 'C-001', 'idempotency_key': 'refund:C-001', 'amount_vnd': 35000, 'status': 'committed'}]


@pytest.mark.parametrize('shape', SHAPES_UNDER_TEST)
def test_changed_quote_conflicts_without_replacing_refund(public_db, tmp_path, monkeypatch, shape):
    monkeypatch.chdir(tmp_path)
    run = SHAPES[shape]
    assert run('C-001', seed=11, store_path=str(public_db)).status == 'resolved'
    conn = connect(public_db)
    try:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 10000 WHERE order_id = (SELECT order_id FROM claims WHERE claim_id = 'C-001')")
        conn.commit()
    finally:
        conn.close()
    result = run('C-001', seed=11, store_path=str(public_db))
    assert (result.status, result.proposal_amount, result.error_reason) == ('failed', 10000, 'amount_conflict')
    ledger, audits, checkpoints = state(public_db)
    assert ledger == [{'idempotency_key': 'refund:C-001', 'amount_vnd': 35000, 'status': 'committed'}]
    assert [a['event_type'] for a in audits].count('refund_committed') == 1
    assert checkpoints[0]['amount_vnd'] == 35000


def test_handoff_filters_facts_and_refuses_write_tools(public_db):
    handoff = make_handoff(request_id='REQ-1', claim_id='C-001', task='investigate',
                           facts={'delay_days': 4, 'parent_secret': 'CANARY_SECRET_FACT',
                                  'raw_headers': {'Authorization': 'Bearer secret'}, 'extra': 'private'},
                           allowed_tools=['lookup_order'])
    assert handoff['facts'] == {'delay_days': 4}
    assert 'secret' not in json.dumps(handoff).lower()
    with pytest.raises(HandoffError):
        make_handoff(request_id='REQ-1', claim_id='C-001', task='investigate', facts={}, allowed_tools=['issue_refund'])
    conn = connect(public_db)
    try:
        with pytest.raises(ToolRejected):
            dispatch(conn, Budget(), 'issue_refund', {'claim_id': 'C-001'}, worker=True)
    finally:
        conn.close()
    assert state(public_db) == ([], [], [])


def test_orchestrator_handoff_and_trace_exclude_parent_context(public_db, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    conn = connect(public_db)
    try:
        conn.execute("UPDATE claims SET parent_secret = ?, raw_headers_json = ?, ticket = ? WHERE claim_id = 'C-001'",
                     ('CANARY_SECRET_PARENT_TEST', '{"Authorization":"RAW_HEADER_TEST"}', 'PRIVATE_TICKET_TEST'))
        conn.execute("UPDATE orders SET phone = ?, address = ?, internal_note = ?, item_name = ? WHERE order_id = (SELECT order_id FROM claims WHERE claim_id = 'C-001')",
                     ('PRIVATE_PHONE_TEST', 'PRIVATE_ADDRESS_TEST', 'PRIVATE_NOTE_TEST', 'PRIVATE_ITEM_TEST'))
        conn.commit()
    finally:
        conn.close()
    captured = []
    real_runner = orchestrator.run_readonly_investigators
    def capture(conn, budget, handoff, principal_id):
        captured.append(json.loads(json.dumps(handoff)))
        return real_runner(conn, budget, handoff, principal_id)
    monkeypatch.setattr(orchestrator, 'run_readonly_investigators', capture)
    result = orchestrator.run_claim('C-001', seed=11, store_path=str(public_db))
    assert result.status == 'resolved'
    assert len(captured) == 1
    assert set(captured[0]) == {'contract_version', 'request_id', 'claim_id', 'principal_scope', 'task', 'facts', 'allowed_tools', 'max_output_tokens'}
    assert captured[0]['facts'] == {}
    assert set(captured[0]['allowed_tools']) == {'lookup_order', 'lookup_policy', 'lookup_refund_history'}
    trace_path = Path(result.trace_path)
    trace = json.loads(trace_path.read_text(encoding='utf-8'))
    assert trace['run_id'] == result.run_id
    assert [event['payload'] for event in trace['events'] if event['kind'] == 'handoff'] == captured
    output = capsys.readouterr()
    artifacts = ''.join(p.read_text(encoding='utf-8') for p in trace_path.parent.glob(result.run_id + '*') if p.is_file())
    for private in ('CANARY_SECRET_PARENT_TEST', 'RAW_HEADER_TEST', 'PRIVATE_TICKET_TEST', 'PRIVATE_PHONE_TEST', 'PRIVATE_ADDRESS_TEST', 'PRIVATE_NOTE_TEST', 'PRIVATE_ITEM_TEST', 'parent_secret', 'raw_headers'):
        assert private not in artifacts + output.out + output.err + json.dumps(result.as_dict()) + json.dumps(captured)
