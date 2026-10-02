"""Golden cases and security properties, run against the stub API.

When the real API exists, point the same checks at it (see evals/golden.py). A failing case there is a bug,
not a reason to edit the fixture.
"""
import pytest
from fastapi.testclient import TestClient

from brain.stub_api.app import app
from evals.golden import run_case
from fixtures.loader import load

client = TestClient(app)
CASES = load()["golden"]
H = lambda p: {"Authorization": f"Bearer dev:{p}"}


@pytest.fixture(autouse=True)
def fresh_state():
    client.post("/sim/reset")
    yield


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_golden_case(case):
    errs = run_case(client, case, lambda ev: client.post("/sim/advance", json={"event_id": ev}))
    assert not errs, errs


def test_requires_auth():
    assert client.post("/v1/ask", json={"question": "hello"}).status_code == 401


def test_forbidden_and_nonexistent_refusals_are_identical():
    a = client.post("/v1/ask", json={"question": "Show me the security incident report from the Q3 breach"},
                    headers=H("sam")).json()
    b = client.post("/v1/ask", json={"question": "Show me the Q9 quantum hologram audit report"},
                    headers=H("sam")).json()
    assert a["refused"] and b["refused"]
    assert a["answer"] == b["answer"]
    assert set(a) == set(b)
    assert a["citations"] == b["citations"] == []


def test_explain_access_is_uniform_for_forbidden_and_missing():
    forbidden = client.get("/v1/explain-access", params={"doc_id": "confluence:SEC/q3-breach-report"}, headers=H("sam"))
    missing = client.get("/v1/explain-access", params={"doc_id": "confluence:SEC/nope"}, headers=H("sam"))
    assert forbidden.json() == missing.json() == {"found": False}


def test_injection_is_sanitized_and_audited():
    r = client.post("/v1/ask", json={"question": "What is the migration status page situation?"}, headers=H("priya")).json()
    assert "ignore all previous instructions" not in r["answer"].lower()
    events = client.post("/v1/audit/query", json={}, headers=H("jordan")).json()["events"]
    assert "possible_injection" in events[-1]["flags"]


def test_audit_chain_verifies_and_detects_tampering():
    for p in ("priya", "sam", "dana"):
        client.post("/v1/ask", json={"question": "What's the status of the database migration?"}, headers=H(p))
    assert client.get("/v1/audit/verify", headers=H("jordan")).json()["ok"] is True
    client.post("/sim/tamper", params={"seq": 2})
    v = client.get("/v1/audit/verify", headers=H("jordan")).json()
    assert v["ok"] is False and v["first_broken_seq"] == 2


def test_audit_query_requires_compliance_role_and_hashes_denied_ids():
    client.post("/v1/ask", json={"question": "Show me the security incident report from the Q3 breach"}, headers=H("sam"))
    assert client.post("/v1/audit/query", json={}, headers=H("sam")).status_code == 403
    events = client.post("/v1/audit/query", json={}, headers=H("jordan")).json()["events"]
    denied = [d for e in events for d in e["decisions"] if not d["allowed"]]
    assert denied and all("doc_id" not in d and d["doc_id_hash"].startswith("sha256:") for d in denied)


def test_stale_answer_alert_after_source_changes():
    client.post("/v1/ask", json={"question": "What's the latest runbook for payment-service incident failover?"},
                headers=H("priya"))
    assert client.get("/v1/alerts", headers=H("priya")).json()["alerts"] == []
    client.post("/sim/advance", json={"event_id": "e1"})
    alerts = client.get("/v1/alerts", headers=H("priya")).json()["alerts"]
    assert alerts and alerts[0]["changed_doc"] == "confluence:PAY/runbook-payment-service"


def test_mywork_differs_per_persona_and_hides_restricted():
    priya = client.get("/v1/mywork", headers=H("priya")).json()
    sam = client.get("/v1/mywork", headers=H("sam")).json()
    assert priya["issues"] and not sam["issues"]
    assert all("SEC-17" not in i["doc_id"] for i in priya["issues"])
