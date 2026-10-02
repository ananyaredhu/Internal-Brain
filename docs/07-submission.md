# 07 · Submission

**Deadline: Fri 16 Oct 2026.** Target freeze **Thu 15 Oct**. Finalists (top 2 per track) announced 23 Oct; Demo Day 3 Nov (TBC).

## Hard requirements (handbook section 8)
- The project must be **original** and **built on CodeBuddy or WorkBuddy**.
- **Proof of product usage is mandatory**: chat screenshots, API call logs, or a written development-process description. Without proof the project does not proceed to scoring.
- Minimum **3 screenshots or a screen recording** of CodeBuddy/WorkBuddy chat logs from the build.

## Required items
| Item | Status | Notes |
|---|---|---|
| Project title | | Name of the AI agent project |
| Short blurb | | **Under 10 words** (hard limit) |
| Project description | | Overview and value proposition; real-world scenario insights (pain points, audience, core problems); solution design (business and technical architecture, **how prompts drive the AI generation**); business value with quantifiable metrics |
| CodeBuddy / WorkBuddy conversation history | | 3+ screenshots or a recording |
| Cover image | | 16:9, recommended 380x216 px (Miora can help) |
| Demo video (optional) | | 5-8 minutes: overview, core features, reflection on the build approach and tool tips for CodeBuddy/WorkBuddy |
| Project link (optional, bonus points) | | Live URL on Tencent Cloud Singapore |

## Track-specific deliverables (Aspire FinTech)
- Live **demo walkthrough** covering the scenarios in [04-scenarios](04-scenarios.md), each with a worked example.
- **Architecture diagram** with trust boundaries and key design trade-offs (see [01-architecture](01-architecture.md)).
- **Complete source code** via a GitHub repository (decide visibility or judge access before the deadline).
- Clearly indicate the chosen case study ("The Internal Brain") at the start of the presentation.

## Where to submit
The handbook gives `tinyurl.com/TCHackathonSGProjectSubmission`. The credits page shows a different link (`forms.gle/CPV5HQELE4x83eBc6`). **Confirm in the WhatsApp group which is current** before submitting.

## Judging (10 criteria x 10 points)
Impact & Relevance · Human-Centered Design · AI Interaction · Technical Execution · Feasibility · Demo & Storytelling · Innovation & Creativity · UX & Accessibility · Responsible AI & Ethics · Overall Quality. The handbook's judging text appears copy-pasted from another event (it mentions schools and game quality); get the real track criteria from the organizers.

## Proof log
Add a row each time you capture proof. Check every screenshot for API keys, tokens and redemption codes **before** adding it. Store approved files under `docs/proof/`.

| Date | Who | Tool and model | What it shows | File |
|---|---|---|---|---|
| | | | | |

Milestones worth capturing: connector scaffold, simulator permission logic, red-team tests, MCP integration, scheduled WorkBuddy digest, deployment.

## Final checklist
- [ ] All seven scenarios pass on the deployed build
- [ ] Leak-CI shows 0 leaks; `/verify` passes and fails correctly on a tampered log
- [ ] Architecture and trust-boundary diagram exported
- [ ] Demo video recorded (5-8 minutes)
- [ ] 3+ proof screenshots approved and logged
- [ ] Title, blurb (<10 words), description, cover image ready
- [ ] No secrets in the repo history (run the secret scan on the full history)
- [ ] Repo access decided; README works from a fresh clone
- [ ] Submitted via the confirmed link
