# Contracts

These files are the **agreements between workstreams**. Code in one workstream depends on these shapes, not on another workstream's internals.

| Contract | Defines | Producer | Consumers |
|---|---|---|---|
| [connector-interface](connector-interface.md) | `Connector` protocol, `Document`, `Chunk`, `AccessDecision` | A | B |
| [acl-model](acl-model.md) | Principals, ACL tokens, per-source semantics, labels on derived artifacts | A (evaluators), B (PDP) | A, B, C |
| [audit-event-schema](audit-event-schema.md) | Audit event fields, hash chain, `/verify` | B | C |
| [context-packet](context-packet.md) | What the LLM plane receives | B | B |
| [skills-format](skills-format.md) | Runtime skill files | B | B, C |
| [api](api.md) | HTTP API used by the UI | B | C |
| [mcp-tools](mcp-tools.md) | MCP tool definitions | B | C (WorkBuddy/CodeBuddy setup) |

## Rules
- **Freeze: Day 3 (Sun 4 Oct).** After that, any change is a PR approved by **all three** (enforced by CODEOWNERS).
- Version each contract with a `version:` line at the top. Bump it on any change and note it in the changelog at the bottom of the file.
- Each workstream ships a **stub** of its side by Day 3, returning fixture data that matches the contract, so the others can build against it.
- Examples in these files are fixtures: copy them into tests.
- Field names are `snake_case`. Timestamps are UTC ISO-8601. IDs are opaque strings.
