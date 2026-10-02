# Agent and contributor conventions

(For CodeBuddy, WorkBuddy, or any coding agent working in this repo. Verify whether CodeBuddy reads `CODEBUDDY.md` instead; if so, copy this file to that name.)

## Ground rules
1. **Docs are the source of truth.** Read `docs/01-architecture.md` and the relevant `docs/02-contracts/*.md` before changing code. If code and a contract disagree, fix the contract in a PR first.
2. **The policy plane has no LLM.** Anything that decides who may see what is plain, deterministic, tested code in `brain/policy/`.
3. **The LLM plane is untrusted.** It gets only sanitized, already-authorized context. No credentials, no network except to the policy plane, no write tools.
4. **Never commit secrets.** Keys live in `.env` (gitignored). `.env.example` has names only. Never paste keys, tokens, or redemption codes into prompts, issues or screenshots.
5. **Denied content never leaves the trust boundary.** Do not send documents the asker may not see to any model or third-party service.
6. **Every derived artifact carries ACL labels** (answers, summaries, caches, memory, vectors). See `docs/02-contracts/acl-model.md`.
7. **Uniform refusals.** A denied document and a nonexistent document must produce the same response shape and similar timing.

## Layout and ownership
`connectors/`, `simulators/` are Workstream A. `brain/`, `mcp_server/` are B. `ui/`, `evals/`, `deploy/` are C. Cross-cutting changes need a PR reviewed by the owner.

## Code
- Python 3.12 for backend, type hints required, `ruff` and `pytest`.
- Every connector implements `docs/02-contracts/connector-interface.md` and must pass the shared contract tests against both real and simulated backends.
- New behavior needs a test; security behavior needs a test in `evals/`.
- Small PRs, one concern each. Reference the workstream task in the PR description.

## Using CodeBuddy / WorkBuddy
- Keep chat logs for the proof log (`docs/07-submission.md`). Screenshot milestones, with keys blurred.
- Do not auto-approve all agent actions. Keep the agent inside this workspace.
- Prefer the free models (Hy3 / Hy4 preview) for routine edits; use the expensive ones sparingly.
