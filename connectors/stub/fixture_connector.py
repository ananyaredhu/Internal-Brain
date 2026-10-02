"""A connector backed by the shared fixtures. For development and as the reference for contract tests.

It is NOT a real or simulated platform: permissions are the token-overlap rule only.
Real connectors and simulators must pass the same contract tests with richer semantics.
"""
from connectors.base import AccessDecision, AclEvidence, Change, ChangeBatch, Document, PlatformIdentity, Source
from fixtures.loader import State, can_see, persona_by_email

POLICY_VERSION = "fixture-0.1"

_SOURCE_PREFIXES = {
    "slack": ("channel:",),
    "jira": ("role:", "group:jira:"),
    "confluence": ("group:confluence:",),
    "gdrive": ("group:gdrive:", "external:"),
}


class FixtureConnector:
    def __init__(self, source: Source, state: State | None = None):
        self.source = source
        self.state = state or State()
        self._log: list[Change] = []
        self._seen_events = 0

    # -- helpers used by tests and the stub API -------------------------------------------------
    def advance(self, event_id: str) -> None:
        ev = self.state.advance(event_id)
        if ev["type"] == "upsert":
            doc = self.state.docs[ev["doc_id"]]
            if doc["source"] == self.source:
                self._log.append(Change("upsert", ev["doc_id"], ev["at"]))
        elif ev["type"] == "acl_change":
            for d in self.state.docs.values():
                if d["source"] == self.source and set(ev["remove_tokens"]) & set(d["acl"]["tokens"]):
                    self._log.append(Change("acl_change", d["doc_id"], ev["at"]))

    # -- Connector protocol ---------------------------------------------------------------------
    def resolve_identity(self, email: str) -> PlatformIdentity | None:
        p = persona_by_email(self.state.data, email)
        if p is None:
            return None
        prefixes = _SOURCE_PREFIXES[self.source]
        toks = self.state.persona_tokens[p["id"]]
        groups = sorted(t for t in toks if t.startswith(prefixes) or t == "public:org")
        return PlatformIdentity(self.source, f"{self.source}-{p['id']}", email, groups)

    def list_changes(self, cursor: str | None) -> ChangeBatch:
        start = int(cursor or 0)
        batch = self._log[start:]
        return ChangeBatch(batch, str(len(self._log)), False)

    def fetch(self, doc_id: str) -> Document:
        d = self.state.docs[doc_id]
        a = d["acl"]
        return Document(
            doc_id=d["doc_id"], source=d["source"], kind=d["kind"], title=d["title"], url=d["url"],
            body=d["body"], parent_id=d["parent_id"], links=list(d["links"]), author=d["author"],
            created_at=d["created_at"], updated_at=d["updated_at"], version=d["version"],
            acl=AclEvidence(list(a["tokens"]), a["native"], a["snapshot_hash"], a["observed_at"]),
        )

    def check_access(self, identity: PlatformIdentity, doc_id: str) -> AccessDecision:
        """Fail closed: unknown docs and unknown identities are denied with the same shape."""
        now = self.state.data["now"]
        d = self.state.docs.get(doc_id)
        p = persona_by_email(self.state.data, identity.email)
        if d is None or p is None or d["source"] != self.source:
            return AccessDecision(False, [], now, "", POLICY_VERSION)
        toks = self.state.persona_tokens[p["id"]]
        if can_see(toks, d):
            hit = sorted(toks & set(d["acl"]["tokens"]))[0]
            return AccessDecision(True, [f"user:{p['email']}", hit], now, d["acl"]["snapshot_hash"], POLICY_VERSION)
        return AccessDecision(False, [], now, d["acl"]["snapshot_hash"], POLICY_VERSION)

    def version(self, doc_id: str) -> str:
        return self.state.docs[doc_id]["version"]
