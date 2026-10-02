"""Load the shared fixture corpus and provide the reference visibility rule.

The reference rule (token overlap) is the *prefilter* from docs/02-contracts/acl-model.md.
The real system also does a just-in-time `check_access`; the fixture connector treats the
token overlap as authoritative.
"""
import copy
import json
from pathlib import Path

_PATH = Path(__file__).with_name("company_a.json")


def load() -> dict:
    return json.loads(_PATH.read_text(encoding="utf-8"))


def persona_by_id(data: dict, persona_id: str) -> dict:
    for p in data["personas"]:
        if p["id"] == persona_id:
            return p
    raise KeyError(persona_id)


def persona_by_email(data: dict, email: str) -> dict | None:
    for p in data["personas"]:
        if p["email"] == email:
            return p
    return None


def can_see(persona_tokens: set[str], doc: dict) -> bool:
    return bool(persona_tokens & set(doc["acl"]["tokens"]))


class State:
    """Mutable copy of the corpus. Events are applied in order with `advance()`."""

    def __init__(self, data: dict | None = None):
        self.data = copy.deepcopy(data or load())
        self.docs = {d["doc_id"]: d for d in self.data["documents"]}
        self.persona_tokens = {p["id"]: set(p["tokens"]) for p in self.data["personas"]}
        self.applied: list[str] = []

    def advance(self, event_id: str) -> dict:
        ev = next(e for e in self.data["events"] if e["id"] == event_id)
        if ev["id"] in self.applied:
            return ev
        if ev["type"] == "upsert":
            self.docs[ev["doc_id"]].update(ev["patch"])
        elif ev["type"] == "acl_change":
            self.persona_tokens[ev["persona"]] -= set(ev["remove_tokens"])
        self.applied.append(ev["id"])
        return ev

    def visible_docs(self, persona_id: str) -> list[dict]:
        toks = self.persona_tokens[persona_id]
        return [d for d in self.docs.values() if can_see(toks, d)]
