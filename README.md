# FAIR — Fabric AI Readiness

A config-driven assessment of Microsoft Fabric and Power BI Copilot estates. It measures four
things that fail independently and have different fixes:

- **Enablement** — are the tenant switches, capacity SKUs, regions and workspace settings in place, and were they set deliberately?
- **Usage** — is anyone asking questions, of which models, how often, and is that measured?
- **Validity & relevance** — are the answers correct, do they address the question asked, and is the AI-visible schema sufficient without being cluttered?
- **Performance & cost** — how broadly does a generated query scan, how long does it take, what does it burn in capacity units?

**138 rules across 15 areas.** Every rule cites a source. 122 are `documented` (stated in Microsoft
documentation, linked); 16 are `inferred` (engineering judgement built on documented behaviour) and
say so, so you can tell published requirements from opinion.

## Why it exists

Left unscoped, Copilot and Fabric data agents reason over every object they can see on every
question — behaving like an ad-hoc SQL server, scanning wide before answering. That degrades
accuracy, latency and cost at the same time. Most rules here bound what the generator can see.

Three documented facts make that concrete rather than a matter of taste:

| Fact | Consequence |
|---|---|
| The DAX generation tool uses **only** the AI data schema | Never define one and the generator considers the full model |
| Indexing caps at **1,000 model entities** and **5M instance values** | A column that would exceed the budget is skipped *entirely*, silently, and not necessarily one you'd have chosen to drop |
| Too large a schema triggers automatic reduction (`AgentSchemaReduced`) | Curation happens either way; the only question is whether you decided what went |

And it is a cost problem: data agent requests bill at **100 CU-seconds per 1,000 input tokens**
(cached: 10) and **400 per 1,000 output tokens**, with the generated query billed separately to its
own engine. Instructions, source instructions, example queries and conversation history are all
input tokens on *every* request.

## What's in here

| Path | What it is |
|---|---|
| `AssessmentRules.json` | **The source of truth.** 138 rules, generated from `rules/`. |
| `assessment-rules.schema.json` | JSON Schema the rule pack validates against |
| `rules/` | Rule fragments; add your own under `rules/custom/` |
| `src/assess.py` | Scoring + findings harness (no dependencies beyond stdlib; `jsonschema` optional) |
| `src/build_rules.py` | `rules/` → `AssessmentRules.json`, with validation |
| `src/build_workbook.py` | → `AssessmentRules.xlsx` |
| `src/build_page.py` | → `readiness-console.html` |
| `AssessmentRules.xlsx` | The same rules as a scoring workbook (generated) |
| `readiness-console.html` | Interactive console (generated) |
| `docs/METHODOLOGY.md` | Scoring model, how to run it, how to extend it, known gaps |
| `samples/` | Blank evidence template, a worked example, and what the harness emits |

Three instruments — the console, the workbook and the CLI — score the same evidence identically.
That equivalence is verified in CI, not assumed.

## Quick start

```bash
# generate a blank evidence file
python3 src/assess.py --rules AssessmentRules.json --template evidence.json

# fill it in, then score it
python3 src/assess.py --rules AssessmentRules.json --evidence evidence.json \
                      --out-json findings.json --out-md findings.md
```

Or open `AssessmentRules.xlsx` and fill the yellow cells — the Scoring tab recalculates live. Or use
the console and export evidence JSON, which feeds `assess.py` directly.

### Gate a release on readiness

```bash
python3 src/assess.py --rules AssessmentRules.json --evidence evidence.json \
                      --fail-on-blocker --fail-under 75
```

Exit `2` if a blocker rule is unmet, `3` if the score is below the threshold.

## Scoring

```
ruleScore    = resultCredit × severityWeight × weightMultiplier
areaScore    = 100 × Σ ruleScore / Σ maxRuleScore      (excluding n/a)
overallScore = Σ (areaScore × areaWeight) / Σ areaWeight
```

Results: `pass` (1.0) · `partial` (0.5) · `fail` (0) · `na` (excluded from both sides) ·
`unknown` (scored 0, reported separately as assessment debt).

**Eight rules are blockers.** If any is `fail` or `unknown`, maturity is forced to level 0 whatever
the numeric score, and the score is reported for trending only — because the average is misleading
when something foundational is missing.

| Level | Score | Meaning |
|---|---|---|
| 0 · Not Ready | 0–39 | Do not expose to business users |
| 1 · Foundational | 40–59 | Works technically; answers unreliable, cost uncontrolled. Closed pilot |
| 2 · Operational | 60–74 | Scoped and governed for a defined question set. Supervised rollout |
| 3 · Optimized | 75–89 | Grounded, narrow, measured. Broad rollout |
| 4 · AI-Ready | 90–100 | Continuously evaluated with regression gates in the pipeline |

## Diagnosing broad-scan behaviour

If the symptom is "it scans everything before answering", work these in order. 1–3 diagnose;
4–9 are the fixes, in rough descending order of effect per unit of effort.

| # | Rule | Check |
|---|---|---|
| 1 | `SCH-001` | Does an AI data schema exist at all? |
| 2 | `SCH-005` | Is `AgentSchemaReduced` appearing? |
| 3 | `PRF-003` | Capture the generated DAX and trace actual scan breadth |
| 4 | `AGT-001` | Do source instructions state default filters, grain, join paths? |
| 5 | `AGT-005` | Is a default time window enforced on KQL sources? |
| 6 | `MEA-007` | Are common calculations pre-built? |
| 7 | `VER-001` | Are recurring questions served by verified answers? |
| 8 | `MOD-001` | Is the model a star schema? |
| 9 | `PRF-005` | Measure tokens per question |

## Extending

Drop `rules/custom/*.json` using the same schema, then rebuild:

```bash
python3 src/build_rules.py      # merges + validates
python3 src/build_workbook.py
python3 src/build_page.py
```

A custom rule whose `id` matches a built-in one **overrides** it — the supported way to change a
threshold to your own standard while keeping the pack updatable. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Known gaps

Stated plainly so nobody mistakes this for complete:

- **No automated collectors.** Each rule's `check.how` describes the procedure; wiring it to the Fabric APIs, Semantic Link Labs and the Capacity Metrics app is work this pack scopes but doesn't do.
- **The platform moves.** Several cited features are preview, and Q&A is announced for retirement in December 2026 while advanced DAX generation currently depends on it (`MET-007` tracks it). Re-verify `documented` limits quarterly.
- **Two published defaults conflict.** Microsoft's Copilot admin settings page and the Power BI enablement page describe the master Azure OpenAI switch as enabled by default; the data agent tenant settings page lists it as off. `TEN-001` carries a note — read your actual tenant state.
- **Latency, scan-breadth and token budgets are deliberately unset.** They depend on your capacity, model size and question mix. The rules require you to set and measure against a budget; they don't invent the number.

## Sources

17 sources, listed with URLs in the `sources` block of `AssessmentRules.json` and on the workbook's
Sources tab. Primarily Microsoft Learn documentation for Copilot in Power BI and Fabric data agents,
plus [chat-with-your-data-solution-accelerator](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator)
and [rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator) for the
evaluation discipline — the accelerators' RAG architecture differs from Fabric's
natural-language-to-DAX path, so what transfers is the measure-tune-remeasure method, not the
retrieval mechanics.

## License

[MIT](LICENSE).
