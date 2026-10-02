# MCP tools

version: 0.1 (draft, freezes Day 3)
Producer: Workstream B. Consumer: C (WorkBuddy and CodeBuddy setup).

The MCP server is **another front door into the same pipeline as the UI**. It contains no separate logic.

## Design
- **Stateless:** Python MCP SDK (FastMCP), streamable HTTP, `stateless_http=True`. No MCP session state. Conversation memory lives in our own store, keyed by `conversation_id`.
- **Per-request identity:** every call carries `Authorization: Bearer <JWT>` from our mock IdP. Validated on every request (signature, expiry, audience). **No shared service credential**, no token passthrough to upstream systems.
- **Narrow, read-only tools.** No raw "run a query" tool. Predefined, constrained tools only.
- **Pinned tool descriptions:** tool descriptions are treated as untrusted by clients; ours are fixed and versioned (tool-poisoning defense).
- Same refusal behavior as the HTTP API: uniform shape, no hints about hidden content.
- Every call is written to the audit log as `mcp_call`.

## Tools
| Tool | Input | Output |
|---|---|---|
| `ask` | `question`, optional `conversation_id`, optional `skill_hint` | Same as `POST /v1/ask` |
| `search` | `query`, optional `sources[]`, `limit` | Authorized hits only: `doc_id`, `title`, `url`, `snippet`, `as_of` |
| `get_source` | `doc_id` | Content of one authorized document, or the uniform "not found" |
| `explain_access` | `doc_id` | `proof_path` for an allowed document, else "not found" |
| `audit_query` | `question` or `filter` | Compliance role only; audit events, `verify` status |

## Client configuration
CodeBuddy (`~/.codebuddy/.mcp.json` or project `.mcp.json`):
```json
{
  "mcpServers": {
    "internal-brain": {
      "type": "http",
      "url": "https://<our-host>/mcp",
      "headers": { "Authorization": "Bearer ${BRAIN_TOKEN}" }
    }
  }
}
```
Keep the token in an environment variable. Never commit it or show it in screenshots. WorkBuddy supports STDIO, SSE and HTTP transports with custom headers: verify in practice (see [06-risks-and-checks](../06-risks-and-checks.md)).

## Use in the demo
- Jordan (compliance) asks the audit question from **WorkBuddy**; a **scheduled WorkBuddy task** produces a weekly compliance digest from `audit_query`.
- Developers query project knowledge from **CodeBuddy** with their own identity.

## Changelog
- 0.1: first draft.
