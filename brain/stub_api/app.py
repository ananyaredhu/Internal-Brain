"""Stub of the Brain HTTP API (docs/02-contracts/api.md, v0.1) backed by the shared fixtures.

Purpose: let Workstream C build the UI and the golden-test harness before Workstream B's real pipeline
exists, and give B a reference for response shapes. It is NOT the real system: retrieval is keyword
overlap, the "LLM" is a template, and permissions are the token-overlap rule only.

Auth (stub only): `Authorization: Bearer dev:<persona_id>`, e.g. `Bearer dev:priya`.
The real API validates a JWT from the mock IdP on every request.

Run: uvicorn brain.stub_api.app:app --reload --port 8000
"""
import hashlib
import json
import re

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from fixtures.loader import State, can_see

app = FastAPI(title="Internal Brain stub API", version="0.1")
STATE = State()
AUDIT: list[dict] = []
ANSWERED: dict[str, list[dict]] = {}   # persona -> [{request_id, doc_ids}]
SALT = "stub-salt"
REFUSAL = "I couldn't find anything you have access to about that."
STOP = {"the", "and", "what", "whats", "were", "was", "there", "that", "this", "with", "from", "show", "have",
        "about", "which", "for", "are", "any", "our", "you", "did", "does", "can", "how", "who", "when", "into"}
INJECTION = re.compile(r"[^.]*ignore (all )?(previous|prior) instructions[^.]*\.?", re.I)


# ---------------------------------------------------------------------------------------------------
def _persona(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer dev:"):
        raise HTTPException(401, "Use 'Authorization: Bearer dev:<persona_id>' with the stub API")
    pid = authorization.removeprefix("Bearer dev:")
    p = next((x for x in STATE.data["personas"] if x["id"] == pid), None)
    if p is None:
        raise HTTPException(401, "unknown persona")
    return p


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 3 and t not in STOP}


def _score(question: str, doc: dict) -> int:
    return len(_tokens(question) & _tokens(doc["title"] + " " + doc["body"]))


def _sanitize(body: str) -> tuple[str, list[str]]:
    if INJECTION.search(body):
        return INJECTION.sub("[removed: possible prompt injection]", body), ["possible_injection"]
    return body, []


def _hash(obj) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _append_audit(event: dict) -> None:
    event["seq"] = len(AUDIT) + 1
    event["ts"] = STATE.data["now"]
    event["prev_hash"] = AUDIT[-1]["hash"] if AUDIT else "genesis"
    event["hash"] = _hash({k: v for k, v in event.items() if k != "hash"})
    AUDIT.append(event)


class AskBody(BaseModel):
    question: str
    conversation_id: str | None = None
    skill_hint: str | None = None


class AdvanceBody(BaseModel):
    event_id: str


# ---------------------------------------------------------------------------------------------------
@app.get("/v1/health")
def health():
    return {"ok": True, "stub": True}


@app.post("/v1/ask")
def ask(body: AskBody, authorization: str | None = Header(None)):
    me = _persona(authorization)
    toks = STATE.persona_tokens[me["id"]]
    scored = sorted(((_score(body.question, d), d) for d in STATE.docs.values()), key=lambda x: -x[0])
    candidates = [(s, d) for s, d in scored if s >= 2][:8]
    allowed = [d for s, d in candidates if can_see(toks, d)][:5]
    denied = [d for s, d in candidates if not can_see(toks, d)]
    request_id = f"req_{len(AUDIT) + 1:04d}"

    claims, citations, flags, lines = [], [], [], []
    for d in allowed:
        text, f = _sanitize(d["body"])
        flags += f
        snippet = text[:200]
        lines.append(f"- {d['title']}: {snippet}")
        claims.append({"text": f"{d['title']}: {snippet}", "citations": [d["doc_id"]]})
        citations.append({"doc_id": d["doc_id"], "title": d["title"], "url": d["url"], "source": d["source"],
                          "as_of": d["updated_at"],
                          "why_visible": [f"user:{me['email']}", sorted(toks & set(d["acl"]["tokens"]))[0]]})

    refused = not allowed
    answer = REFUSAL if refused else "Here is what I found:\n" + "\n".join(lines)
    ANSWERED.setdefault(me["id"], []).append({"request_id": request_id, "doc_ids": [d["doc_id"] for d in allowed]})

    decisions = [{"doc_id": d["doc_id"], "allowed": True, "proof_path": c["why_visible"],
                  "acl_snapshot_hash": d["acl"]["snapshot_hash"], "policy_version": "stub-0.1",
                  "doc_version": d["version"], "jit_checked": True} for d, c in zip(allowed, citations, strict=True)]
    decisions += [{"doc_id_hash": _hash([SALT, d["doc_id"]]), "allowed": False, "reason": "no_access",
                   "acl_snapshot_hash": d["acl"]["snapshot_hash"], "policy_version": "stub-0.1"} for d in denied]
    _append_audit({"request_id": request_id, "event_type": "ask",
                   "actor": {"user_id": me["email"], "roles": me["roles"], "client": "ui"},
                   "query": {"text": body.question, "skill": body.skill_hint},
                   "decisions": decisions,
                   "answer": {"text": answer, "sha256": _hash(answer), "citations": [c["doc_id"] for c in citations],
                              "refused": refused},
                   "flags": sorted(set(flags))})
    return {"request_id": request_id, "conversation_id": body.conversation_id or "c_1", "answer": answer,
            "claims": claims, "citations": citations, "refused": refused, "abstained": False,
            "freshness": {"oldest_source_as_of": min((c["as_of"] for c in citations), default=None),
                          "stale_refetched": 0},
            "skill": body.skill_hint}


@app.get("/v1/mywork")
def mywork(authorization: str | None = Header(None)):
    me = _persona(authorization)
    vis = STATE.visible_docs(me["id"])
    return {
        "user": {"display_name": me["display_name"], "roles": me["roles"]},
        "issues": [{"doc_id": d["doc_id"], "title": d["title"]} for d in vis if d["source"] == "jira"],
        "projects": sorted({d["parent_id"] for d in vis if d["source"] == "jira"}),
        "channels": sorted({d["parent_id"] for d in vis if d["source"] == "slack"}),
        "recent_pages": [{"doc_id": d["doc_id"], "title": d["title"], "updated_at": d["updated_at"]}
                         for d in sorted((x for x in vis if x["source"] in ("confluence", "gdrive")),
                                         key=lambda x: x["updated_at"], reverse=True)[:5]],
        "suggested_questions": [g["question"] for g in STATE.data["golden"] if g["persona"] == me["id"]][:3],
        "alerts": alerts(authorization)["alerts"],
    }


@app.get("/v1/explain-access")
def explain_access(doc_id: str, authorization: str | None = Header(None)):
    me = _persona(authorization)
    d = STATE.docs.get(doc_id)
    toks = STATE.persona_tokens[me["id"]]
    if d is None or not can_see(toks, d):
        return {"found": False}   # identical for forbidden and nonexistent
    return {"found": True, "proof_path": [f"user:{me['email']}", sorted(toks & set(d["acl"]["tokens"]))[0]]}


@app.get("/v1/alerts")
def alerts(authorization: str | None = Header(None)):
    me = _persona(authorization)
    out = []
    for ev_id in STATE.applied:
        ev = next(e for e in STATE.data["events"] if e["id"] == ev_id)
        if ev["type"] != "upsert":
            continue
        for ans in ANSWERED.get(me["id"], []):
            if ev["doc_id"] in ans["doc_ids"]:
                out.append({"request_id": ans["request_id"], "changed_doc": ev["doc_id"],
                            "changed_at": ev["at"], "summary": ev.get("note", "A source changed after your answer")})
    return {"alerts": out}


@app.post("/v1/audit/query")
def audit_query(body: dict, authorization: str | None = Header(None)):
    me = _persona(authorization)
    if "compliance" not in me["roles"]:
        raise HTTPException(403, "compliance role required")
    user = (body.get("filter") or {}).get("user")
    events = [e for e in AUDIT if user is None or e["actor"]["user_id"] == user]
    return {"events": events, "count": len(events)}


@app.get("/v1/audit/verify")
def audit_verify(authorization: str | None = Header(None)):
    _persona(authorization)
    prev = "genesis"
    for e in AUDIT:
        body = {k: v for k, v in e.items() if k != "hash"}
        if e["prev_hash"] != prev or e["hash"] != _hash(body):
            return {"ok": False, "first_broken_seq": e["seq"], "reason": "hash mismatch"}
        prev = e["hash"]
    return {"ok": True, "checked": len(AUDIT), "checkpoints": 0}


@app.get("/v1/freshness")
def freshness(authorization: str | None = Header(None)):
    _persona(authorization)
    return {"sources": {s: {"lag_p50_s": 20, "lag_p95_s": 90, "last_sync": STATE.data["now"]}
                        for s in ("slack", "gdrive", "confluence", "jira")}}


@app.get("/v1/leakci/latest")
def leakci(authorization: str | None = Header(None)):
    _persona(authorization)
    return {"as_of": STATE.data["now"], "cases": len(STATE.data["golden"]), "leaks": 0, "stub": True}


# --- stub-only simulation helpers (the real equivalents are simulator admin endpoints, owned by A) -------------
@app.post("/sim/advance")
def sim_advance(body: AdvanceBody):
    STATE.advance(body.event_id)
    return {"applied": STATE.applied}


@app.post("/sim/reset")
def sim_reset():
    global STATE
    STATE = State()
    AUDIT.clear()
    ANSWERED.clear()
    return {"ok": True}


@app.post("/sim/tamper")
def sim_tamper(seq: int):
    AUDIT[seq - 1]["query"]["text"] = "TAMPERED"
    return {"tampered": seq}
