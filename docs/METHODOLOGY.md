# Fabric AI Readiness Assessment — methodology

Rule pack `2026.09.1` · 138 rules · 15 areas · spec `1.0.0`

## What this measures

Four things, deliberately kept separate because they fail independently and have different fixes:

1. **Enablement** — are the tenant switches, capacity SKUs, regions and workspace settings actually in place, and were they set deliberately.
2. **Usage** — is anyone asking questions, of which models, how often, and is that measured.
3. **Validity and relevance** — are the answers correct, do they address the question asked, and is the AI-visible schema sufficient without being cluttered.
4. **Performance and cost** — how broadly does a generated query scan, how long does it take, and what does it burn in capacity units.

The organising idea across all four is **scope reduction**. A Copilot or data agent surface that has not been narrowed reasons over every object it can see on every question. That produces the behaviour you want to avoid — the system acting like an ad-hoc SQL server, scanning wide before returning — and it degrades accuracy, latency and cost simultaneously. Most rules in this pack are, directly or indirectly, about bounding what the generator can see.

## Why scope reduction is the spine

Three documented facts make this concrete rather than a matter of taste:

- The DAX generation tool uses **only** the AI data schema. If you never define one, the generator considers the full model.
- Power BI indexes at most **1,000 model entities** and **5 million instance values**. When the next column would exceed the instance-value budget, that column is **skipped entirely** — silently, and not necessarily the column you would have chosen to drop.
- When the schema is too large to render, Copilot **reduces it automatically** and flags `AgentSchemaReduced` in diagnostics. At that point schema curation is happening whether you did it or not; the only question is whether you or the platform decided what went.

A fourth fact makes it a cost problem too: data agent requests bill at **100 CU seconds per 1,000 input tokens** and **400 per 1,000 output tokens**, and instructions, source instructions, example queries and conversation history are all input tokens on **every single request**. The query the agent then generates is billed separately to its own engine. Verbosity is not free once; it is expensive forever.

## The rule schema

Every rule is a JSON object. The fields that matter when you extend the pack:

| Field | Purpose |
|---|---|
| `id` | `AAA-000`. Area prefix plus sequence. Use your own prefix (`ORG-001`) for custom rules. |
| `area` | One of the 15 areas. Determines which weight applies and which workbook tab it lands on. |
| `requirement` | The normative statement — what must be true. |
| `rationale` | Why it matters for enablement, answer quality, or query cost. |
| `severity` | `blocker` \| `critical` \| `high` \| `medium` \| `low`. Drives the scoring weight. |
| `check` | `method` (how evidence is gathered), `how` (the actual procedure), plus `operator`/`threshold`/`unit` where the rule is numeric. |
| `limit` | Present only where the rule encodes a platform limit. Carries `value`, `unit`, and `hard` — a hard limit is enforced by the platform, a soft one is guidance. |
| `remediation` | What to do about a failure. |
| `impactIfViolated` | What goes wrong if you don't. |
| `sourceIds` | Keys into the `sources` block. Every rule cites at least one. |
| `verified` | `documented` (stated in a cited source), `inferred` (engineering judgement built on cited behaviour), or `community`. |
| `weightMultiplier` | Optional. Used sparingly to weight a few rules above their severity band. |

### On `verified`

Read this field before you argue with a threshold. **122 of 138 rules are `documented`** — the requirement is stated in Microsoft documentation and the source is linked. **16 are `inferred`** — reasonable practice built on documented platform behaviour, but not something Microsoft published as a rule. Every numeric threshold that Microsoft did not publish (the 40% verified-answer coverage target, the 90% golden-set promotion gate) is flagged `inferred` and says so in its own unit string. Calibrate those to your risk appetite; treat the `documented` limits as authoritative but re-verify them against current docs, because this platform moves.

## Scoring

```
ruleScore    = resultCredit × severityWeight × weightMultiplier
areaScore    = 100 × Σ ruleScore / Σ maxRuleScore      (excluding n/a)
overallScore = Σ (areaScore × areaWeight) / Σ areaWeight
```

**Result states:** `pass` (credit 1.0) · `partial` (0.5) · `fail` (0) · `na` (excluded from both numerator and denominator) · `unknown` (scored as 0 but reported separately as assessment debt).

`unknown` scoring as zero is intentional. An unassessed control is not a passing control, and separating it out in the report stops "we haven't looked yet" from hiding inside "we're at 60%".

**Severity weights:** blocker 13 · critical 8 · high 5 · medium 3 · low 1.

**Area weights** are set so that scope reduction (14), semantic model structure (12), metadata (11), and the three areas covering agent config, validity and tenant/capacity enablement (10 each) dominate. That is a deliberate statement that curation and grounding matter more than polish.

### The blocker gate

Eight rules carry `severity: blocker`. If any of them is `fail` or `unknown`, **overall maturity is forced to level 0 regardless of the numeric score**, and the score is reported for trending only. This exists because the numeric average is misleading when something foundational is missing — a tenant with perfect metadata, no AI data schema and no golden question set can score in the sixties while being entirely unfit to expose to users.

The eight blockers: the Copilot/Azure OpenAI tenant switch (`TEN-001`), cross-geo processing where the region requires it (`TEN-002`), minimum paid SKU (`CAP-001`), same-region agent and sources (`CAP-002`), an explicitly defined AI data schema (`SCH-001`), Q&A enabled on the model (`MET-006`), RLS defined for sensitive data (`SEC-001`), and a golden question set with expected answers (`VAL-001`).

### Maturity levels

| Level | Name | Score | What it means |
|---|---|---|---|
| 0 | Not Ready | 0–39.99 | Do not expose to business users. Blocking enablement or trust gaps. |
| 1 | Foundational | 40–59.99 | Works technically, but answers are unreliable and cost is uncontrolled. Closed pilot only. |
| 2 | Operational | 60–74.99 | Scoped and governed for a defined question set. Supervised department rollout. |
| 3 | Optimized | 75–89.99 | Grounded, narrow, measured. Repeatable answers, bounded query cost. Broad rollout. |
| 4 | AI-Ready | 90–100 | Continuously evaluated against a golden set with regression gates in the pipeline. |

## Running an assessment

### 1. Bound the scope

Name the tenant, the capacities, the semantic models and the data agents. An assessment without a scope statement produces a score nobody can act on, because nobody knows what it covers. Record it in the `scope` block of the evidence file or on the workbook's Readme tab.

### 2. Choose your instrument

**Workbook** — for a walkthrough with people in the room. One tab per area, yellow cells only, live scoring on the Scoring tab. Best when the assessment is a conversation with model owners.

**JSON + harness** — for repeatable and automated assessment. Generate the evidence template, fill it in, run the harness, commit the findings alongside the model.

```bash
python3 assess.py --rules AssessmentRules.json --template evidence.json
# fill in evidence.json
python3 assess.py --rules AssessmentRules.json --evidence evidence.json \
                  --out-json findings.json --out-md findings.md
```

For CI, `--fail-on-blocker` exits 2 when a blocker is unmet and `--fail-under 75` exits 3 below a threshold, so a model can be blocked from promotion on its own readiness score.

The two instruments compute identical scores — that equivalence is verified, not assumed.

### 3. Collect evidence by method

The `check.method` field tells you where to look:

| Method | Where the evidence comes from |
|---|---|
| `admin-portal` | Fabric Admin Portal — tenant settings, capacity delegated settings |
| `api` | Fabric/Power BI REST APIs, scanner API, Semantic Link Labs |
| `dax` | `INFO.*` DAX functions against the model — objects, relationships, descriptions, properties |
| `tmdl` | The model definition in source control — TMDL/LSDL inspection |
| `vpax` | VertiPaq Analyzer / Semantic Model Memory Analyzer extract — cardinality, size, unused objects |
| `metrics` | Fabric Capacity Metrics app — AI Query operations, LlmPlugin item kind |
| `trace` | Query trace during golden-set execution — scan breadth, storage engine events, duration |
| `manual` | Inspection, interview, or document review |

Record *where* the evidence lives, not just the verdict. A `pass` with no evidence reference is an opinion, and it will not survive the next assessment when the person who made the call has moved on.

### 4. Interpret the result

Read in this order:

1. **Blocker gate.** If it fired, nothing else matters yet. Fix those first.
2. **The lowest-scoring areas by weight.** A 30% score in schema (weight 14) costs more than a 30% in datatype (weight 5).
3. **Assessment debt.** A large `unknown` count means the score is not yet a measurement.
4. **The remediation plan.** Ordered by severity then weight, so working top-down is close to optimal.

### 5. Fix in dependency order

The rules have a natural sequence, and the documented implementation workflow follows it:

**Optimize the model for performance** → **define the AI data schema** → **create verified answers** → **add AI instructions in Prep for AI** → **bind to the agent** → **verify the generated DAX** → **configure agent-level instructions for cross-source concerns only** → **validate and iterate** → **put it all under source control**.

Doing these out of order wastes effort. Writing descriptions before trimming the schema means documenting objects you are about to remove. Tuning instructions before fixing the star schema means compensating in prose for a structural problem.

## Diagnosing broad-scan behaviour specifically

If the presenting symptom is "it scans everything before answering", work these rules in order:

| Step | Rule | What you are checking |
|---|---|---|
| 1 | `SCH-001` | Does an AI data schema exist at all, or is the full model exposed? |
| 2 | `SCH-005` | Is `AgentSchemaReduced` appearing? The platform is already truncating for you. |
| 3 | `PRF-003` | Capture the generated DAX and trace it. Measure actual scan breadth per question. |
| 4 | `AGT-001` | Do source instructions state default filters, grain and join paths? |
| 5 | `AGT-005` | For KQL and time-series sources, is a default time window enforced? |
| 6 | `MEA-007` | Are common calculations pre-built, or is the generator composing time intelligence from scratch each time? |
| 7 | `VER-001` | Are the top recurring questions served by verified answers instead of regenerating? |
| 8 | `MOD-001` | Is the model a star schema? A flat model makes efficient DAX hard to generate at all. |
| 9 | `PRF-005` | Measure tokens per question. Trim instructions and examples; exploit cached input at a tenth the rate. |

Steps 1–3 diagnose. Steps 4–9 are the fixes, roughly in descending order of effect per unit of effort.

## Improving validity and relevance

Score correctness and relevance separately (`VAL-002`, `VAL-003`), then classify every failure into one of three causes (`VAL-004`):

- **Recall failure** — a required object was missing from the AI-visible schema. Fix: add that specific object back.
- **Precision failure** — a distracting object misled the generator. Fix: remove that object.
- **Generation failure** — the schema was right and the DAX was still wrong. Fix: a pre-built measure or a verified answer.

The discipline that matters: **never respond to a failure by widening the schema generally**. That is how a carefully curated model drifts back to scanning everything within two release cycles. Every schema change should name the object it adds or removes and the question that justified it.

This taxonomy is adapted from RAG evaluation practice — context recall and context precision — where the retrieved context is the AI data schema rather than a set of document chunks. The mechanics differ; the diagnostic value transfers.

Then treat every configuration change as an experiment (`VAL-010`): record the configuration version, what changed, and the resulting accuracy, relevance, latency and tokens-per-question. Revert what does not earn its place. Without this log, configuration accretes on intuition and nothing can safely be removed.

## Extending the pack

Drop additional rule files into `rules/custom/*.json` using the same schema and rebuild:

```bash
python3 build_rules.py        # merges, validates, writes AssessmentRules.json
python3 build_workbook.py     # regenerates the workbook
```

Custom rules matching an existing `id` **override** the built-in rule of that id — that is the supported way to change a threshold to your own standard while keeping the pack updatable. Add a new area by adding it to `areaWeights` and `AREA_TITLES` in the builder.

The builder validates ids, severities, areas, source references and required fields, and fails the build on any error. The workbook is a generated view, never the source of truth.

## Known gaps

Stated plainly so nobody mistakes this pack for complete:

- **Automated collectors are not included.** `check.how` describes the procedure for each rule; wiring it to the Fabric APIs, Semantic Link Labs and the Capacity Metrics app is implementation work this pack scopes but does not do.
- **The platform moves fast.** Several cited features are in preview, and Q&A is announced for retirement in December 2026 while advanced DAX generation currently depends on it (`MET-007` tracks this). Re-verify `documented` limits each quarter.
- **Two published defaults conflict.** Microsoft's Copilot admin settings page and the Power BI enablement page describe the master Azure OpenAI switch as enabled by default; the data agent tenant settings page lists it as off. `TEN-001` carries a note about this — read your actual tenant state rather than assuming either.
- **Thresholds for latency, scan breadth and tokens-per-question are deliberately unset.** They depend on your capacity, model size and question mix. The rules require you to set and measure against a budget; they do not invent the number for you.

## Sources

All 17 sources are listed with URLs in the `sources` block of `AssessmentRules.json` and on the workbook's Sources tab. Every rule cites at least one.
