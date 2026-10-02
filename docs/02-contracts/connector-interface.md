# Connector interface

version: 0.1 (draft, freezes Day 3)
Producer: Workstream A. Consumers: B (ingestion, PDP, JIT checks).

Every source (Slack, Google Drive, Confluence, Jira), real or simulated, implements the same protocol and passes the same **contract tests**. Simulators must be proven faithful by running the same tests against the real API wherever one exists.

## Protocol (Python)
```python
from typing import Protocol, Literal, Iterable

Source = Literal["slack", "gdrive", "confluence", "jira"]

class Connector(Protocol):
    source: Source

    def resolve_identity(self, email: str) -> "PlatformIdentity | None":
        """Map a corporate email to this platform's identity (Slack user ID, Jira accountId...)."""

    def list_changes(self, cursor: str | None) -> "ChangeBatch":
        """Incremental changes since cursor (created/updated/deleted docs AND permission changes)."""

    def fetch(self, doc_id: str) -> "Document":
        """Current content, links and ACL evidence for one document."""

    def check_access(self, identity: "PlatformIdentity", doc_id: str) -> "AccessDecision":
        """Authoritative, live answer: may this identity read this doc right now?
        Called just-in-time by the PDP. Must be fast (<300 ms typical) and cacheable by the caller (short TTL)."""

    def version(self, doc_id: str) -> str:
        """Cheap source version (etag / updated timestamp) used to detect staleness."""
```

## Data types
```python
class PlatformIdentity:
    source: Source
    platform_user_id: str
    email: str
    groups: list[str]          # platform-native groups, roles, channels, as the platform sees them

class Document:
    doc_id: str                # globally unique: "<source>:<native id>"
    source: Source
    kind: str                  # page | issue | message | thread | file | comment
    title: str
    url: str
    body: str                  # text content (markdown ok)
    parent_id: str | None      # space/project/channel/folder container
    links: list[str]           # doc_ids this doc references (cross-platform links allowed)
    author: str
    created_at: str
    updated_at: str
    version: str
    acl: "AclEvidence"

class AclEvidence:
    tokens: list[str]          # effective allow tokens at observed_at (see acl-model.md)
    native: dict               # source-native raw ACL data kept for audit and replay
    snapshot_hash: str         # sha256 of canonical(native)
    observed_at: str

class ChangeBatch:
    changes: list["Change"]
    next_cursor: str
    has_more: bool

class Change:
    type: Literal["upsert", "delete", "acl_change"]
    doc_id: str
    detected_at: str

class AccessDecision:
    allowed: bool
    proof_path: list[str]      # minimal grant path, e.g. ["user:priya", "group:payments-eng", "space:PAY"]
    evaluated_at: str
    acl_snapshot_hash: str
    policy_version: str
```

## Chunk (indexed unit, written by A's ingestion, read by B's retrieval)
```python
class Chunk:
    chunk_id: str
    doc_id: str
    position: int
    text: str
    acl_tokens: list[str]      # copied from the document's AclEvidence
    acl_snapshot_hash: str
    source_version: str        # Document.version at index time
    embedding: list[float]
    embedding_model: str       # e.g. "bge-m3"
    embedding_version: str
    ingested_at: str
```
Vectors carry the **same ACL tokens as their chunk** and are never shared across ACLs.

## Behavior requirements
- `list_changes` must also emit `acl_change` entries when permissions change (channel removal, page restriction, folder share change), not only content changes.
- Deleted or no-longer-visible docs must be reported so they can be dropped from the index.
- `check_access` must never return `allowed=True` on an error or timeout: **fail closed**.
- Rate limits: connectors back off and surface lag as a metric (`freshness_lag_seconds`).
- Credentials are read-only, least-privilege, and live only in the connector process.

## Contract tests (`connectors/tests/contract/`)
1. Seeded fixture: known docs with known ACLs, expected `fetch`, `version` and `check_access` results per persona.
2. Revocation: change the ACL, then `list_changes` emits `acl_change` and `check_access` flips to deny within the SLA.
3. Edit: change content, then `version` changes and `list_changes` emits `upsert`.
4. Inheritance: container-level permissions apply to children (Confluence space to page, Drive folder to file).
5. Negative: `check_access` for a nonexistent doc and for a forbidden doc return the same shape.

## Changelog
- 0.1: first draft.
