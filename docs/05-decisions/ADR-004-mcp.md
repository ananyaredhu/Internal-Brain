# ADR-004 · Stateless MCP server

**Status:** Accepted.

## Context
MCP servers are a known leakage vector: shared service credentials, confused-deputy problems, and authorization checked only at session start. We want CodeBuddy and WorkBuddy to act as real clients with per-user identity.

## Decision
- **Stateless:** Python MCP SDK (FastMCP), streamable HTTP, `stateless_http=True`.
- **Per-request identity:** every call carries a bearer JWT from our mock IdP, validated per request (signature, expiry, audience). No token passthrough to upstream systems; no shared master key.
- **Narrow, read-only tools** (`ask`, `search`, `get_source`, `explain_access`, `audit_query`). No raw "run a query" tool.
- Pinned, versioned tool descriptions. Every call audited as `mcp_call`.
- MCP is another front door into the same pipeline as the UI, with no separate logic.
- Conversation memory lives in our own store, not in MCP sessions.

## Consequences
- Per-request authorization, easy scaling, simple deployment.
- No server-initiated streaming or subscriptions. If later needed, add a stateful path separately.
- Clients: CodeBuddy supports `type: http` servers with `headers` and `${ENV}` variables; WorkBuddy documents STDIO, SSE and HTTP transports with custom headers.

## To verify
WorkBuddy remote MCP with an Authorization header and scheduling work in practice (check #7); which instruction file CodeBuddy reads (check #8).
