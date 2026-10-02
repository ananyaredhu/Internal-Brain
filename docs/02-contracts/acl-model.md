# ACL model

version: 0.1 (draft, freezes Day 3)
Owners: A (per-source evaluators), B (policy decision point, labels on derived artifacts).

## Principle: do not flatten
Each platform has its own permission semantics. We normalize **only for fast prefiltering**, and always keep the source-native evidence. The authoritative answer is the connector's live `check_access`.

## Tokens
An ACL token names a principal that has effective read access. A chunk's `acl_tokens` is the set of principals who may read it at `observed_at`.

| Token | Meaning |
|---|---|
| `user:<email>` | A specific person |
| `group:<source>:<id>` | A platform group, role or team, e.g. `group:confluence:security-team` |
| `channel:<slack id>` | Members of a Slack channel |
| `role:<project>:<role>` | A Jira project role |
| `public:org` | Anyone in the organization |
| `external:<email>` | A specific external person (Drive external sharing) |

The asker's **access token set** is computed from their resolved identities: their `user:` token, their groups from every platform, channel memberships, project roles, `public:org`. Prefilter: `chunk.acl_tokens && asker_tokens` (array overlap, GIN index).

Deny rules (Jira issue security levels, Confluence page restrictions that narrow inherited access) are **resolved at index time** into the effective allow set. The JIT check catches anything the prefilter gets wrong.

## Per-source semantics (what the evaluator must honor)
| Source | Semantics |
|---|---|
| **Confluence** | Space permissions, plus page restrictions (view/edit) that narrow access; restrictions inherit from ancestor pages; anonymous/public spaces |
| **Jira** | Project permission scheme via project roles and groups; **issue security levels** restrict individual issues (e.g. security-sensitive bugs visible only to the security team) |
| **Slack** | Public channels (workspace members), private channels (members only), DMs (participants only); threads follow their channel; external/guest users restricted to their channels |
| **Google Drive** | Folder and file sharing (viewer/commenter/editor), inheritance from folders, shared drives vs personal drives, link sharing, external sharing for some folders |

Simulators must implement these rules, not simplified versions. The contract tests prove it.

## Identity mapping
The IdP (mock OIDC) issues a JWT with `sub` and `email`. `resolve_identity(email)` maps it to each platform's user and groups. Missing mapping = **no access on that platform** (fail closed).

## Labels on derived artifacts (information-flow control)
Every derived artifact carries `acl_label`: the **intersection** of the ACL tokens of all sources it was derived from.
Derived artifacts: answers, summaries, cache entries, conversation memory, context profiles, vectors, stale-answer alerts.
Rule: an artifact may be served to a user only if the user's access token set satisfies **every** source in its derivation (i.e. the user is authorized for each underlying source). If any source is no longer visible to them, the artifact is not served.

## Decisions are recorded with evidence
Each allow/deny decision stores: `doc_id`, `allowed`, `proof_path`, `acl_snapshot_hash`, `policy_version`, `doc_version`, `evaluated_at`. This enables replay ("was this decision correct at the time?") and time-travel queries.

## Uniform refusal
A denied document and a nonexistent one produce the same response shape, similar timing, and no counts or titles. Link-edge expansion follows a link only if the target passes the PDP.

## Changelog
- 0.1: first draft.
