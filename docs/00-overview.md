# 00 · Overview

## The challenge (Aspire, FinTech track)
Build an **Internal Brain**: an AI system that unifies context across **Confluence, Jira, Slack and Google Drive**, answers natural-language questions with citations, and enforces each platform's access controls end to end, with a tamper-evident audit trail.

Company knowledge is scattered; staff lose about 30% of their week searching. But "an assistant that can read everything can leak everything", so every answer must be scoped to what the asker may see, and every retrieval and answer must be recorded.

### What the handbook requires
- Heterogeneous source integration that **does not flatten** each platform's permission model.
- **Permission-aware retrieval:** know the asker, filter *before* the LLM sees anything, and handle permissions changed after ingestion.
- Cross-platform context assembly with permission checks on every piece.
- Security logging and audit: tamper-evident, complete (who, what, retrieved IDs, answer, time, allow/deny per document), queryable.
- LLM safety: mitigate the model "filling in" content it was not given.
- Five scenarios, each with a worked example: see [04-scenarios](04-scenarios.md).
- Deliverables: live demo, architecture and trust-boundary diagram with trade-offs, full source on GitHub.

## Thesis
> **The model proposes, a deterministic policy plane disposes.**
The LLM never sees unauthorized content, holds no credentials and has no write tools. Every claim in an answer traces to a chunk that was authorized at read time, and every decision is written to a hash-chained audit log.

## What is new here (calibrated)
Already common in 2026, so **not** claimed as new: query-time ACL filtering (Glean, Onyx Enterprise, Microsoft Copilot), hash-chained agent audit libraries, general discussion of MCP identity propagation.

What we add:
1. **Answer-level ACL labels.** Every derived artifact (answer, summary, cache entry, memory, vector) carries the intersection of its sources' ACLs.
2. **Closed, measured revocation window.** Re-verify at read time and publish revocation-to-enforcement time.
3. **Link-edge authorization.** Follow cross-platform links only if the target is also authorized.
4. **Post-generation leakage scan** against the denied set, run locally, with canary strings for testing.
5. **Replayable authorization audit.** Entries store the ACL snapshot hash and policy version; time-travel queries ("what could X see on date D?") with proof paths.
6. **Noninterference CI ("Leak-CI").** A user's answer must not change when documents they cannot see are added, removed or edited. Tested metamorphically.
7. **Stale-answer alerts.** If a source behind an answer changes, notify the people who received it.
8. **Identity-propagating, stateless MCP server.** CodeBuddy and WorkBuddy become real clients, with per-user identity and no shared master key.
9. **Red-team harness with a public scoreboard.**

We cannot prove nothing like this exists; we claim only that we found these gaps open in the products and papers we checked.

## Scope
Everything in tiers 1 to 3 is in scope; the tiers set **build order**, not what to cut.
- **Tier 1 (core):** connectors, policy decision point, retrieval, query path, five scenarios, audit chain, UI, deployment.
- **Tier 2 (differentiators):** Leak-CI, answer-level ACL labels, stale-answer alerts, replayable audit.
- **Tier 3:** runtime skills, context profile and context engineering, MCP server, My Work home.
- **Stretch:** sensitivity-aware model routing, mosaic/aggregation guard, honeytoken documents, voice (TRTC), access receipts for users.

About 45 person-days of work for 3 people over 15 days; the risk is schedule. A **demoable build by Day 8** and a schedule review then.

## Judging map (10 criteria x 10 points)
| Criterion | Where we score |
|---|---|
| Impact & Relevance | 30% search-time problem plus the "can it leak everything" fear |
| Human-Centered Design | Persona UI, "why can I see this?" explanations, My Work |
| AI Interaction | Routing, context engineering, skills, checker, MCP |
| Technical Execution | Policy plane, JIT checks, hash chain, contract tests, evals |
| Feasibility | Real connectors where free, production path (OpenFGA/SpiceDB, real tenants) |
| Demo & Storytelling | Split-screen personas across all scenarios |
| Innovation | The list above |
| UX & Accessibility | Keyboard, ARIA, high contrast, optional voice |
| Responsible AI & Ethics | Zero-leak, abstention, red-team scoreboard, audit |
| Overall Impression | Polish, live URL, demo video |

Track-specific criteria are shared after registration: ask in the track's WhatsApp group.

## Tencent products (mandatory and optional)
- **Mandatory:** the project must be built on **CodeBuddy or WorkBuddy**, with proof (3+ screenshots or recordings of chat logs). We use both. See [07-submission](07-submission.md).
- **Optional:** ADP (agent platform, DeepSeek models), TRTC ASR/TTS (voice), Miora (visuals), Hunyuan models/embeddings, Tencent Cloud Singapore for hosting.
