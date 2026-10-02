# Runtime skills format

version: 0.1 (draft, freezes Day 3)
Owner: Workstream B. Consumers: B (router and loader), C (admin view).

A **skill** makes the agent specific to a task: a procedure, an output format and an allowlist of tools. Skills are instructions only. **A skill never carries authority**: it cannot widen access, add tools beyond its allowlist, or change policy.

(Not to be confused with build-time CodeBuddy skills, which help us develop the project. Those live with the developer's tooling.)

## Layout
```
brain/skills/<name>/
  SKILL.md            frontmatter + procedure
  templates/          optional output templates
  examples/           optional few-shot examples (fixture-safe, no real data)
```

## `SKILL.md`
```markdown
---
name: incident-investigation
version: 1
description: Find the root cause of an incident and list follow-up tickets
triggers: ["root cause", "outage", "incident", "postmortem"]
sources: [jira, slack, confluence, gdrive]
tools_allowlist: [search, get_source, explain_access]
output_schema: claims_with_citations_v1
max_evidence: 12
---
# Procedure
1. Identify the incident from the question and the user's recent focus.
2. Gather the incident ticket, the incident Slack thread, the postmortem and the runbook.
3. State the root cause only if a cited source states it. Otherwise say it is not established.
4. List follow-up tickets with status and owner, each cited.
# Constraints
- Cite every claim. Abstain on anything unsupported.
- Never infer the existence of content you were not given.
```

## Loading and routing
- The router (small model) picks a skill from `triggers` and `description`, or none (default procedure).
- The loader reads the skill and injects its procedure into the system prompt. Output must conform to `output_schema`.
- Skills are **versioned and reviewed** like code (PR required). A skill is a prompt-injection surface, so skill files are never writable at runtime and are pinned by hash in the audit log (`skill`, `skill_version`).

## First four skills
| Skill | Serves |
|---|---|
| `status-and-blockers` | Scenario 1 (DB migration status plus Slack blockers) |
| `incident-investigation` | CTO question 1 (outage root cause plus follow-up tickets) |
| `design-discussion-summary` | CTO question 2 (auth-service design threads plus decision doc link) |
| `audit-inquiry` | Scenario 5 (what did user X access); compliance role only |

## Changelog
- 0.1: first draft.
