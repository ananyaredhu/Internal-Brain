"""Shared connector types. Mirrors docs/02-contracts/connector-interface.md (v0.1).

Real connectors, simulators and the fixture connector all implement `Connector`.
Change the contract doc first (PR with all three reviewers), then this file.
"""
from dataclasses import dataclass, field
from typing import Literal, Protocol

Source = Literal["slack", "gdrive", "confluence", "jira"]


@dataclass
class PlatformIdentity:
    source: Source
    platform_user_id: str
    email: str
    groups: list[str] = field(default_factory=list)


@dataclass
class AclEvidence:
    tokens: list[str]
    native: dict
    snapshot_hash: str
    observed_at: str


@dataclass
class Document:
    doc_id: str
    source: Source
    kind: str
    title: str
    url: str
    body: str
    parent_id: str | None
    links: list[str]
    author: str
    created_at: str
    updated_at: str
    version: str
    acl: AclEvidence


@dataclass
class Change:
    type: Literal["upsert", "delete", "acl_change"]
    doc_id: str
    detected_at: str


@dataclass
class ChangeBatch:
    changes: list[Change]
    next_cursor: str
    has_more: bool = False


@dataclass
class AccessDecision:
    allowed: bool
    proof_path: list[str]
    evaluated_at: str
    acl_snapshot_hash: str
    policy_version: str


class Connector(Protocol):
    source: Source

    def resolve_identity(self, email: str) -> PlatformIdentity | None: ...

    def list_changes(self, cursor: str | None) -> ChangeBatch: ...

    def fetch(self, doc_id: str) -> Document: ...

    def check_access(self, identity: PlatformIdentity, doc_id: str) -> AccessDecision: ...

    def version(self, doc_id: str) -> str: ...
