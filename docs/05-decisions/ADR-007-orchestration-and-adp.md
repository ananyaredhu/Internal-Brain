# ADR-007 · Orchestration: LangGraph; ADP as an optional backend

**Status:** Accepted.

## Context
We need an orchestration layer where deterministic policy gates are clearly separate from LLM steps, and where the pipeline is easy to trace and demo. Tencent's Agent Development Platform (ADP) offers workflows, a knowledge base, DeepSeek models, and publishes agents with a shareable Experience URL and an AppKey-protected Chat API.

## Decision
- **LangGraph** for the pipeline: explicit state, typed nodes, deterministic policy gates as plain-code nodes, traces for demos.
- **ADP is not the core.** Its knowledge base is a general RAG store with platform, space, application and knowledge-base permissions. It does not ingest per-user ACLs from Confluence, Jira, Slack or Drive, so uploading documents there would bypass our permission model.
- ADP may be used (a) as one model backend behind the gateway, called only with already-authorized context, and/or (b) to publish an Experience URL for judges. Its Chat API calls a published ADP app with its own prompt; it is not a raw completion endpoint, so generator and checker call model endpoints directly.

## Consequences
- Tencent product use is real but optional beyond the mandatory CodeBuddy/WorkBuddy.
- A free ADP allowance (knowledge base capacity, DeepSeek tokens) can fund some model calls: confirm the amount and expiry in Platform Management.
- Keep AppKeys out of the repo and screenshots.

## To verify
ADP free quota; whether per-request context can be passed through its Chat API.
