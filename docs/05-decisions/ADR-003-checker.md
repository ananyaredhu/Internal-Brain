# ADR-003 · Layered answer checker

**Status:** Accepted.

## Context
Even with correct retrieval, the generator might add unsupported claims or echo content it should not have. A checker from the same model family as the generator would share its blind spots. DeepSeek-R1 as a fallback checker is the same family and slow.

## Decision
Three layers behind the model gateway, cheapest and most independent first.
1. **Deterministic checks (always):** every cited source exists and is visible to the asker; a **local denied-set leakage scan** compares the answer with documents the user was denied (names, IDs, phrases, and optionally local bge-m3 similarity). No LLM involved.
2. **Small purpose-built grounding model, run locally:** MiniCheck-style claim-versus-document verification, from a different family than the generator.
3. **Small open-weight chat model for hard cases only:** Qwen 3B to 8B, or open Hunyuan small models.
If support is missing at any layer: abstain or redact.

## Consequences
- The denied-set scan is **always local**; denied content is never sent to any model or third party.
- The claim check only ever sees authorized content, so a hosted model would be acceptable for layer 3 if CPU is too slow.
- Time layers 2 and 3 on the deployment server's CPU on Day 3; use a 3B to 4B model if 8B is too slow.
- Canary strings in restricted documents make the leak scan testable in Leak-CI.

## To verify
Grounding model names and licenses (from memory); CPU timing; whether open Hunyuan small models are available.
