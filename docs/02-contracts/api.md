# HTTP API

version: 0.1 (draft, freezes Day 3)
Producer: Workstream B. Consumer: C (UI, console). The MCP server exposes the same pipeline: see [mcp-tools](mcp-tools.md).

Base path `/v1`. JSON. **Auth:** `Authorization: Bearer <JWT>` from the mock IdP on **every** request (validated per request: signature, expiry, audience). JWT claims: `sub`, `email`, `roles`, `aud`.

Errors: `{ "error": {"code": "...", "message": "..."} }`. Refusals are **not errors**: they return 200 with `refused: true` and the uniform refusal shape.

## `POST /v1/ask`
Request: `{ "question": "...", "conversation_id": "optional", "skill_hint": "optional" }`
Response:
```json
{
  "request_id": "req_9f2c",
  "conversation_id": "c_1",
  "answer": "...",
  "claims": [{"text": "...", "citations": ["jira:DBMIG-142"]}],
  "citations": [{"doc_id": "jira:DBMIG-142", "title": "...", "url": "...", "source": "jira", "as_of": "2026-10-10T13:58:00Z", "why_visible": ["role:DBMIG:developer"]}],
  "refused": false,
  "abstained": false,
  "freshness": {"oldest_source_as_of": "...", "stale_refetched": 0},
  "skill": "status-and-blockers"
}
```
Refusal: `{ "refused": true, "answer": "I couldn't find anything you have access to about that.", "claims": [], "citations": [] }`. Same shape and similar timing for forbidden and nonexistent content. No counts, no titles.

## `GET /v1/mywork`
Personalized home for the logged-in user: assigned issues, projects, recent pages, channels, suggested questions, pending stale-answer alerts. Everything is fetched through the PDP: nothing the user cannot see.

## `GET /v1/explain-access?doc_id=...`
Why can I see this? Returns `proof_path` for an allowed document. For a forbidden or nonexistent one, returns the uniform "not found" response.

## `GET /v1/alerts`
Stale-answer alerts: answers the user received whose sources changed afterwards (`request_id`, `changed_doc`, `changed_at`, `summary`).

## Audit (compliance role only)
- `POST /v1/audit/query` with `{ "question": "..." }` (natural language) or `{ "filter": {user, space, from, to, decision} }` returns events, with timestamps, retrieved IDs and allow/deny decisions.
- `GET /v1/audit/verify` returns `{ok, checked, checkpoints}` or `{ok:false, first_broken_seq, reason}`.
- `GET /v1/audit/time-travel?user=...&at=...` returns what a user could see at a past time (when bi-temporal ACL snapshots are available).

## Admin and ops (admin role)
- `GET /v1/freshness` returns lag p50/p95 per source and last sync.
- `GET /v1/leakci/latest` returns the latest Leak-CI and red-team scoreboard.
- `GET /v1/health`.

## Demo and test helpers (simulators only, never in production)
Simulator admin endpoints (owned by A) to revoke a permission, restrict a page, edit a document, and add or remove hidden documents (for Leak-CI). Documented in `simulators/README.md`.

## Changelog
- 0.1: first draft.
