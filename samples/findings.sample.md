# Fabric AI Readiness Assessment - findings

*Rule pack 2026.09.1 - assessed 2026-09-10T16:22:28+00:00*

**Scope:** tenant: Contoso, capacities: F64-PROD-EUS, semanticModels: Sales Analytics, Finance Core, dataAgents: Sales Insights Agent, assessor: Mary Mary

## Readiness: Not Ready (level 0)

**Weighted score: 53.2 / 100**

> Maturity is gated at level 0: 2 blocker rule(s) not met. The numeric score of 53.2 is reported for trending only.

| Blocker | Rule | Result |
|---|---|---|
| `SCH-001` | An AI data schema is explicitly defined for every in-scope semantic model | fail |
| `VAL-001` | A golden question set exists with expected answers | fail |

Do not expose Copilot or data agents to business users. Blocking enablement or trust gaps present.

## Summary

- Rules evaluated: **138**
- Open findings (fail or partial): **74**
- Not yet assessed: **7**
- Open by severity: blocker 2, critical 24, high 30, medium 15, low 3

## Area scores

| Area | Score | Weight | Rules | Pass | Partial | Fail | N/A | Unknown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Performance & query efficiency | 5.5 | 9 | 8 | 1 | 0 | 6 | 0 | 1 |
| Response validity & relevance | 24.6 | 10 | 13 | 4 | 3 | 6 | 0 | 0 |
| Verified answers | 28.4 | 6 | 7 | 1 | 1 | 5 | 0 | 0 |
| Measures & DAX | 37.3 | 9 | 12 | 3 | 4 | 5 | 0 | 0 |
| AI instructions | 37.9 | 6 | 5 | 1 | 2 | 1 | 0 | 1 |
| AI data schema & scope reduction | 42.5 | 14 | 21 | 6 | 6 | 9 | 0 | 0 |
| Names, descriptions & linguistics | 48.2 | 11 | 10 | 3 | 2 | 4 | 0 | 1 |
| Semantic model structure | 50.9 | 12 | 10 | 4 | 3 | 2 | 0 | 1 |
| Data types & data quality | 52.3 | 5 | 5 | 2 | 1 | 1 | 0 | 1 |
| Workspace & item governance | 52.9 | 6 | 7 | 3 | 2 | 0 | 0 | 2 |
| Operations, ALM & adoption | 60.3 | 6 | 7 | 4 | 1 | 2 | 0 | 0 |
| Fabric data agent configuration | 68.6 | 10 | 10 | 5 | 3 | 2 | 0 | 0 |
| Security, RLS & compliance | 89.2 | 8 | 8 | 6 | 1 | 1 | 0 | 0 |
| Capacity, SKU, region & cost | 92.0 | 10 | 6 | 5 | 1 | 0 | 0 | 0 |
| Tenant & admin enablement | 100.0 | 10 | 9 | 9 | 0 | 0 | 0 | 0 |

## Remediation plan (81 items, most severe first)


### Blocker

**`VAL-001` A golden question set exists with expected answers** - _fail_
- Requirement: Each model or agent in scope must have a maintained golden question set with agreed correct answers, covering the declared question scope including edge cases and known-ambiguous phrasings.
- Fix: Build it from real user questions, agree the correct answer with the business data owner, and version it alongside the model.
- If not fixed: Quality is anecdotal, regressions are invisible, and every tuning decision is a guess.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md); [microsoft/rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator)

**`SCH-001` An AI data schema is explicitly defined for every in-scope semantic model** - _fail_
- Requirement: Every semantic model exposed to Copilot or bound to a data agent must have an AI data schema defined through Prep data for AI, rather than defaulting to the full model surface.
- Fix: Open Prep data for AI > Simplify the data schema and deselect every field not required by the intended question set.
- If not fixed: The generator considers every table, column and measure on every question - maximum latency, maximum token cost, maximum ambiguity.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Prepare your data for AI to improve Copilot results (preview)](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)


### Critical

**`PRF-003` Generated DAX is inspected for scan breadth on representative questions** - _fail_
- Requirement: For each question in the golden set, the generated DAX must be captured and reviewed for storage engine scan breadth - unfiltered fact scans, missing date filters, and full-column materialization.
- Fix: Where scans are broad, fix the cause: a missing default filter in instructions, a missing pre-built measure, or a missing verified answer.
- If not fixed: Exactly the ad-hoc-SQL-server behaviour - full scans returned as conversational answers, at full capacity cost.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`VAL-002` Answer accuracy is scored against the golden set each release** - _fail_
- Requirement: Every release must score the golden question set and record the pass rate, with a defined minimum for promotion to production.
- Fix: Gate promotion on the threshold. The 90 percent figure is a working default to be calibrated to your risk appetite, not a Microsoft-published number.
- If not fixed: Model or configuration changes silently degrade answers between releases.
- owner platform-team
- Source (inferred): [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md); [microsoft/rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator); Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`VAL-004` Grounding sufficiency is scored - context precision and recall** - _fail_
- Requirement: Each golden question must be scored for whether the AI-visible schema contained everything needed to answer it and nothing that misled it.
- Fix: Recall failures mean adding back a specific object. Precision failures mean removing one. Generation errors mean a verified answer or a pre-built measure. Never respond to a failure by widening the schema generally.
- If not fixed: Schema is widened reflexively after every failure, which is how models drift back to scanning everything.
- owner platform-team
- Source (inferred): [microsoft/rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator); Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`VAL-005` Generated DAX is reviewed for every golden question, not just the result** - _partial_
- Requirement: Validation must inspect the generated DAX query in each response, not only whether the returned number looks right.
- Fix: Where the DAX is wrong, identify whether the fix belongs in the model, the AI data schema, verified answers or AI instructions.
- If not fixed: Coincidentally correct answers that fail on the next variation of the same question.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`VAL-010` Configuration changes are evaluated as controlled experiments** - _partial_
- Requirement: Changes to AI data schema, instructions, examples or verified answers must be evaluated by re-running the golden set and comparing scores against the prior configuration, one variable at a time where practical.
- Fix: Keep a tuning log: configuration version, what changed, accuracy, relevance, latency, tokens per question. Revert changes that do not earn their place.
- If not fixed: Configuration accretes on intuition; nobody can say which settings are actually helping and none can safely be removed.
- owner platform-team
- Source (inferred): [microsoft/rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator); [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md)

**`CAP-005` Private Link and closed-network constraints are checked** - _partial_
- Requirement: Confirm that in-scope capacities do not depend on Private Link or closed-network configurations that are unsupported for Copilot.
- Fix: Carve the AI-enabled workspaces out of the Private Link enforcement scope, or accept that Copilot is unavailable there.
- If not fixed: Copilot silently unavailable despite every switch appearing correct.
- owner platform-team
- Source (documented): [Enable Fabric Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi)

**`INS-001` AI instructions exist and carry business context** - _partial_
- Requirement: AI instructions must be configured with industry and business context, key terminology definitions, table and field mapping guidance, measure specifications and synonyms, and audience prioritization rules.
- Fix: Structure the instructions on the documented template, then test with real questions.
- If not fixed: The generator has no map from business vocabulary to model objects.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)

**`INS-002` AI instructions are configured in Prep for AI, not at data agent level, for semantic models** - _partial_
- Requirement: For semantic model sources, AI instructions must be set in Prep for AI. Data agent level instructions are ignored for semantic model DAX generation.
- Fix: Move semantic model guidance into Prep for AI; keep agent instructions for formatting, routing, abbreviations and tone across sources.
- If not fixed: Instructions written, paid for in tokens, and ignored by the generator.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`MEA-001` Explicit measures exist for every metric users will ask about** - _fail_
- Requirement: Every business metric within the question scope must be implemented as an explicit DAX measure.
- Fix: Create the measures, name them the way the business names them, and describe them.
- If not fixed: Invented aggregations that do not match the organization's official definition.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`MEA-005` Near-duplicate measures are eliminated or clearly differentiated** - _fail_
- Requirement: The AI schema must not expose several measures meaning approximately the same thing - Total Sales, Sales Amount, Revenue - unless each carries a description that makes the distinction explicit.
- Fix: Keep one canonical measure per concept. Where variants are genuinely needed, encode the distinction in the name and describe it.
- If not fixed: Inconsistent answers to the same business question, which is the fastest route to losing executive trust.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`MEA-006` Measures are named in business language, not technical shorthand** - _fail_
- Requirement: Measure and column names must be descriptive business terms - Average Customer Rating rather than AvgRating, Total Revenue rather than TR_AMT, Sales Region rather than DIM_GEO_01.
- Fix: Rename in the semantic layer. Source-system names belong in Power Query, not in the AI-visible model.
- If not fixed: The generator has no basis for mapping a user's words to your fields.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data); [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MET-002` The essential content of every description sits in the first 200 characters** - _fail_
- Requirement: Descriptions must front-load their meaning: only the first 200 characters are used by Copilot, and semantic model property descriptions are truncated at 200 characters.
- Fix: Rewrite so the first sentence carries the definition and the usage note. Treat 200 characters as the whole budget, not a soft target.
- If not fixed: The disambiguating half of your documentation is silently discarded, and the model looks documented while behaving as if it is not.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data); [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MOD-001` Model follows a star schema with distinct fact and dimension tables** - _partial_
- Requirement: AI-facing semantic models must use a star schema with clearly separated fact and dimension tables; flat denormalized tables and pivoted structures must be avoided.
- Fix: Refactor into conformed dimensions and narrow fact tables. Unpivot wide tables so each row is one observation.
- If not fixed: Inefficient generated DAX, longer scans, higher CU burn per question, and lower answer accuracy.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data); [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MOD-005` A marked date table with hierarchies exists** - _fail_
- Requirement: The model must contain a dedicated date dimension with a logical drill hierarchy - Year > Quarter > Month > Day - and it must be marked as the date table.
- Fix: Add and mark a conformed date dimension; remove auto date/time tables that clutter the AI-visible schema.
- If not fixed: Time-intelligence questions fail or return wrong periods - the most common category of user-facing Copilot error.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`OPS-006` Data reachable by AI is reviewed against the access model** - _fail_
- Requirement: Before a source is exposed to an AI surface, confirm that its contents are appropriate for every user who can reach that surface, given the effective permission model.
- Fix: Where content is not suitable for the widest reader, either narrow the audience or enforce RLS and re-test through the AI path per SEC-002.
- If not fixed: Conversational access materially widens the effective reach of sensitive content.
- owner platform-team
- Source (documented): [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md); Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`PRF-001` The semantic model is performance-tuned before any AI tuning begins** - _unknown_
- Requirement: Semantic model performance optimization must be completed before Prep for AI configuration, and it is step one of the documented implementation workflow.
- Fix: Run the Best Practice Analyzer and the Semantic Model Memory Analyzer, fix what they surface, then start AI configuration.
- If not fixed: Every AI question inherits the model's existing slowness and multiplies it by the generator's less efficient DAX.
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`PRF-005` Token cost per question is measured and budgeted** - _fail_
- Requirement: Average input and output tokens per question must be measured per agent, converted to CU seconds, and tracked against a budget.
- Fix: Trim instructions and examples, exploit cached input where prompt prefixes are stable - cached input is billed at a tenth of the uncached rate - and shift recurring questions to verified answers.
- If not fixed: Per-question cost drifts upward invisibly until the capacity throttles.
- owner platform-team
- Source (documented): [Data agent consumption](https://learn.microsoft.com/en-us/fabric/fundamentals/data-agent-consumption)

**`SCH-002` Model entity count stays within the 1,000-entity indexing ceiling** - _partial_
- Requirement: The combined count of tables and columns in the model should stay at or below 1,000 entities, or the AI data schema must reduce the exposed surface to below that ceiling.
- Fix: Trim the model, or narrow the AI data schema so the AI-visible entity count is well under the ceiling. Aim materially below 1,000, not at it.
- If not fixed: Columns are skipped during indexing; Copilot cannot resolve filter values it should be able to find.
- owner platform-team
- Source (documented): [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)

**`SCH-005` Copilot Diagnostics shows no AgentSchemaReduced warning** - _partial_
- Requirement: Copilot Diagnostics must not report 'AgentSchemaReduced' for in-scope models under representative questions.
- Fix: Reduce the AI data schema yourself until the warning clears, so schema reduction is a deliberate curation decision rather than an automatic truncation.
- If not fixed: Silent, uncontrolled loss of schema; answers omit data that exists and nobody can explain why.
- owner platform-team
- Source (documented): [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)

**`SCH-009` AI data schema is scoped to a declared question set** - _fail_
- Requirement: Each AI data schema must be traceable to a written statement of the question scope the model is meant to serve, and every included object must be justified by at least one question in that scope.
- Fix: Write the scope statement first, derive the schema from it, and reject additions that no scoped question requires.
- If not fixed: Schema sprawl returns within two release cycles and undoes every other tuning effort.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`SCH-010` Data agent object selection matches the model's AI data schema** - _partial_
- Requirement: For a semantic model bound to a data agent, the tables selected in the data agent must be the same tables defined in the model's Prep for AI AI data schema.
- Fix: Reconcile the two selections and add a check to the release process so they cannot drift.
- If not fixed: Objects visible to the agent but absent from the generation schema produce failed or nonsensical DAX.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`SCH-011` Dependent objects of selected measures are included in the schema** - _fail_
- Requirement: When a measure is included in the AI data schema, every object it depends on must also be included.
- Fix: Add the missing dependencies, or drop the measure from the schema if its dependencies must stay hidden.
- If not fixed: Generated DAX references objects the generator believes exist and the query errors.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`SCH-020` Data agent stays within the five data source limit and uses the minimum needed** - _partial_
- Requirement: A data agent must be bound to no more than five data sources, and to the fewest sources that its question scope actually requires.
- Fix: Split broad agents into several narrowly scoped agents rather than binding more sources to one.
- If not fixed: At the cap, source routing errors dominate; beyond it, configuration is rejected.
- owner platform-team
- Source (documented): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)

**`VER-004` No verified answer references a hidden column** - _fail_
- Requirement: Verified answers must not reference hidden columns or measures.
- Fix: Unhide the referenced object or rebuild the verified answer on a visible equivalent.
- If not fixed: Verified answers silently never fire and the team concludes the feature does not work.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`WSP-004` 'Approved for Copilot' is applied through a real review, not by default** - _partial_
- Requirement: Every semantic model marked 'Approved for Copilot' must have passed a documented review covering schema scoping, descriptions, verified answers and a golden-question test pass.
- Fix: Define the approval checklist from this rule pack and gate the flag behind it.
- If not fixed: The approval badge becomes noise and users cannot tell prepared models from unprepared ones.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [Copilot and Agent admin settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-copilot)


### High

**`AGT-004` Agent instructions are reserved for cross-source concerns** - _partial_
- Requirement: Agent-level instructions must cover only cross-source guidance - formatting, source routing, abbreviations and tone - with source-specific logic held at the source or in Prep for AI.
- Fix: Relocate source-specific content and keep the agent layer thin.
- If not fixed: Instructions that are simultaneously ignored where needed and billed everywhere.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`AGT-005` Time filters are required for KQL and time-series sources** - _fail_
- Requirement: For KQL and Eventhouse sources, agent instructions must direct the inclusion of time filters, and users must be guided to include a time range in their questions.
- Fix: Set an explicit default such as the last 7 days unless the user states otherwise, and have the agent state the window it used.
- If not fixed: Full-retention scans on every time-series question, at severe latency and CU cost.
- owner platform-team
- Source (documented): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`AGT-009` Agents are split by subject area rather than consolidated** - _partial_
- Requirement: Where the question scope spans several unrelated subject areas, separate narrowly scoped agents must be used instead of one agent bound to the maximum five sources.
- Fix: Split by subject area; accept more agents in exchange for narrower reasoning per question.
- If not fixed: Routing errors and latency scale with source count on every question.
- owner platform-team
- Source (inferred): [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices); [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`DAT-002` Categorical values are standardized** - _fail_
- Requirement: Values in AI-visible categorical columns must be standardized - Open, Closed, Pending - without mixed case, trailing whitespace, or synonym variants of the same state.
- Fix: Normalize in the transformation layer and add a data quality test to keep it normalized.
- If not fixed: Filters match a subset of the rows they should, producing understated numbers that look valid.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`DAT-005` High-cardinality columns are identified and justified** - _partial_
- Requirement: High-cardinality columns must be identified with the Semantic Model Memory Analyzer and either removed, or justified and excluded from the AI data schema.
- Fix: Remove, bucket, or exclude from the AI schema. A transaction ID needs no place in a natural-language surface.
- If not fixed: Index budget exhausted by columns nobody asks about, starving the ones they do.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`INS-003` Instructions are focused and specific rather than long and complex** - _fail_
- Requirement: AI instructions must be kept focused and specific; conflicting or overly complex instructions must be avoided.
- Fix: Cut instructions to the rules that changed behaviour in testing. Measure the token cost per request before and after.
- If not fixed: Higher latency, higher CU burn on every question, and lower accuracy.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Data agent consumption](https://learn.microsoft.com/en-us/fabric/fundamentals/data-agent-consumption)

**`INS-004` Instructions map user terminology to model objects** - _unknown_
- Requirement: Instructions must explicitly map the terms users say to the tables, measures and columns they mean, including synonyms and abbreviations.
- Fix: Build the mapping from observed user language, not from the data dictionary.
- If not fixed: Correct questions in the users' own words routed to the wrong table.
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`MEA-003` Default summarization is set correctly on numeric columns** - _partial_
- Requirement: Every AI-visible numeric column must have a deliberate default summarization - Sum, Average or None - rather than the inherited default.
- Fix: Set summarizeBy to None on identifiers, years and ratios; set Sum or Average deliberately elsewhere.
- If not fixed: Summed percentages and averaged keys presented as fact.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`MEA-007` Commonly requested measures are pre-built rather than left to generation** - _partial_
- Requirement: Frequently requested calculations - YTD, month-over-month growth, prior-year comparison, run rate - must exist as measures instead of relying on the generator to compose them.
- Fix: Build the top time-intelligence and comparison measures explicitly. Each one removes a whole class of generation errors.
- If not fixed: The generator writes time intelligence from scratch on every question, slowly and sometimes wrongly.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`MET-003` Descriptions state usage guidance, not just a restatement of the name** - _fail_
- Requirement: Descriptions must add information the name does not already carry - what the measure means, when to use it, what to pair it with, and any caveat.
- Fix: Follow the pattern: definition, then usage guidance. For example, year-over-year difference in orders, used with Date[Year] to show years other than the latest.
- If not fixed: Description coverage looks complete on a report while delivering no disambiguation.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`MET-004` Descriptions are prioritized where names are ambiguous** - _unknown_
- Requirement: Descriptions must be present for abbreviated or generic object names, columns holding codes, flags, units or category values, date columns tied to a specific business event, and any object in a large schema.
- Fix: Work the priority list before chasing blanket coverage.
- If not fixed: Effort spread evenly while the genuinely ambiguous objects stay undocumented.
- Source (documented): [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`MET-005` Synonyms are populated in the linguistic schema** - _fail_
- Requirement: Business synonyms and alternative phrasings must be registered in the model's linguistic schema for AI-visible objects.
- Fix: Harvest synonyms from actual user questions and support tickets rather than inventing them.
- If not fixed: Users phrase questions in their own vocabulary and Copilot fails to map it.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models); [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`MOD-003` Ambiguous relationship paths are eliminated** - _partial_
- Requirement: The model must not contain ambiguous relationship paths between AI-visible tables.
- Fix: Deactivate redundant relationships and expose the alternate path through an explicit measure using USERELATIONSHIP.
- If not fixed: Same question, different answer, depending on the path chosen.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`MOD-004` Role-playing relationships are marked inactive and surfaced through measures** - _partial_
- Requirement: Role-playing dimension relationships must be marked inactive where appropriate, with active/inactive state clearly specified.
- Fix: Create measures such as Sales by Ship Date using USERELATIONSHIP, and name them so the role is obvious.
- If not fixed: Date-based questions silently resolve against the wrong date role.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`MOD-006` Ambiguous date columns carry explicit default guidance** - _fail_
- Requirement: Where a model exposes several date columns - Order Date, Ship Date, Due Date - AI instructions or verified answers must state which is the default for each question type.
- Fix: Add an explicit line to AI instructions, for example: unless the user names a date type, use Order Date.
- If not fixed: Revenue questions answered on ship date; the numbers look plausible and are wrong.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`MOD-008` Unused tables, columns and measures are removed** - _unknown_
- Requirement: Objects not required by any report or by the AI question scope must be removed from the model.
- Fix: Delete them, or at minimum hide and exclude them from the AI data schema.
- If not fixed: Higher token cost per question and more ways for the generator to go wrong.
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`OPS-003` A named owner exists per AI-enabled model and agent** - _partial_
- Requirement: Every AI-enabled semantic model and every data agent must have a named business owner and a named technical owner.
- Fix: Assign owners as a precondition of AI enablement.
- If not fixed: Quality issues raised by users go unaddressed and trust decays.
- owner platform-team
- Source (inferred): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`PRF-002` Best Practice Analyzer runs as a gate, not an occasional review** - _fail_
- Requirement: The Best Practice Analyzer must run against every in-scope model on each release, with results triaged and material findings resolved before deployment.
- Fix: Wire BPA into the release pipeline and fail the build on the rule categories you have agreed matter.
- If not fixed: Known-bad patterns accumulate and directly inflate AI query cost.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`PRF-004` A latency budget exists per question class and is measured** - _fail_
- Requirement: An explicit response-time budget must be set per question class and measured against real traffic.
- Fix: Where the budget is breached, narrow the AI data schema and trim instructions before considering capacity increases.
- If not fixed: Latency regressions go unnoticed until users abandon the feature.
- owner platform-team
- Source (inferred): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`PRF-007` Aggregation-first answering is the instructed default** - _fail_
- Requirement: Instructions must direct the agent to aggregate, rank or top-N by default rather than returning detail rows, unless the user explicitly asks for detail.
- Fix: State it explicitly, and have the agent name the aggregation it chose so users can challenge it.
- If not fixed: Wide, expensive result sets truncated to 25 rows and presented as complete.
- owner platform-team
- Source (inferred): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`PRF-008` AI-driven capacity events are correlated with AI usage** - _fail_
- Requirement: Throttling and overload events on AI-enabled capacities must be investigated with AI Query consumption included in the correlation.
- Fix: Add AI Query to the standard capacity incident runbook.
- If not fixed: Repeated incidents misattributed to refresh scheduling while the real driver is AI adoption.
- owner platform-team
- Source (documented): [Overview of Copilot in Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-fabric-overview); [Data agent consumption](https://learn.microsoft.com/en-us/fabric/fundamentals/data-agent-consumption)

**`SCH-006` Surrogate keys and relationship identifiers are removed from the AI schema** - _fail_
- Requirement: Unique identifier columns used only to define relationships must be deselected from the AI data schema.
- Fix: Deselect them in Simplify the data schema. Relationships still work; the generator just stops seeing the keys.
- If not fixed: Grouping by meaningless identifiers, wasted index budget, and joins the generator invents rather than follows.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`SCH-008` Archived, staging and audit tables are excluded** - _fail_
- Requirement: Archived, staging, audit and unrelated tables must be excluded from both the AI data schema and any data agent object selection.
- Fix: Remove them from selection. If they must stay in the model for lineage, hide them and exclude them from the AI schema.
- If not fixed: The generator queries a staging copy and returns numbers that do not tie to any published report.
- owner platform-team
- Source (documented): [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`SCH-018` Prep for AI edits deployed via Git or pipelines are followed by a refresh** - _fail_
- Requirement: After deploying LSDL or Prep for AI changes through Git integration or deployment pipelines, the model must be refreshed in the Power BI service to sync the changes.
- Fix: Add the refresh to the release pipeline and verify the AI configuration post-deployment rather than assuming it landed.
- If not fixed: Deployed AI configuration silently inactive in production.
- owner platform-team
- Source (documented): [Prepare your data for AI to improve Copilot results (preview)](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)

**`SCH-021` Lakehouse content is exposed as tables, not files** - _fail_
- Requirement: Data intended for agent consumption from a Lakehouse must be registered as tables; standalone files are not accessible.
- Fix: Ingest the files as Delta tables before binding the Lakehouse to the agent.
- If not fixed: The agent cannot see data the user can see in OneLake.
- owner platform-team
- Source (documented): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)

**`SEC-004` Agent permission model is understood - read access, not Build** - _partial_
- Requirement: The agent access design must reflect that a Power BI semantic model source requires only Read permission, not Build, and that the agent operates with the consuming user's read access.
- Fix: Re-derive the access design from actual permission requirements and re-test with a least-privileged account.
- If not fixed: Broader effective access than the security design intended.
- owner platform-team
- Source (documented): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)

**`VAL-003` Answer relevance is scored separately from accuracy** - _fail_
- Requirement: Responses must be scored for relevance - did the answer address the question asked - separately from numeric correctness.
- Fix: Relevance failures point at instructions and terminology mapping; correctness failures point at the model and measures. Route each to the right fix.
- If not fixed: Tuning effort aimed at the wrong layer.
- owner platform-team
- Source (inferred): [microsoft/rag-experiment-accelerator](https://github.com/microsoft/rag-experiment-accelerator); [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md)

**`VAL-006` Non-determinism is measured by repeat testing** - _fail_
- Requirement: A subset of golden questions must be asked repeatedly to measure answer variance across runs.
- Fix: For every high-consequence question showing variance, create a verified answer. That converts a probabilistic answer into a deterministic one.
- If not fixed: Two executives ask the same question and get different numbers, which ends the programme.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models); [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`VAL-011` User feedback is captured and routed into the tuning backlog** - _fail_
- Requirement: Thumbs up and down feedback must be collected, reviewed on a defined cadence, and converted into schema, instruction or verified answer changes.
- Fix: Review negative feedback each sprint, classify by the VAL-004 failure taxonomy, and act on the classification.
- If not fixed: The strongest available signal about real-world quality is discarded.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model)

**`VER-002` Each verified answer carries five to seven trigger questions** - _fail_
- Requirement: Every verified answer should define roughly five to seven trigger questions covering natural variations in phrasing, including both formal and conversational wording.
- Fix: Harvest real phrasings from usage logs and support requests rather than writing variations from imagination.
- If not fixed: Verified answers exist but rarely fire, so the tuning effort produces no measurable benefit.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`VER-005` Verified answers are re-saved after any referenced object is renamed** - _fail_
- Requirement: Renaming a table, column or measure referenced by a verified answer requires updating and re-saving that verified answer.
- Fix: Add verified answer revalidation to the rename checklist and to the release pipeline.
- If not fixed: A cosmetic rename silently disables the curated answers protecting your top questions.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`VER-007` Verified answer coverage is measured against actual question volume** - _partial_
- Requirement: The proportion of real user questions answered by a verified answer rather than by generation must be measured and tracked over time.
- Fix: Feed the miss list back into verified answer creation each cycle. The threshold here is a working target, not a Microsoft-published figure.
- If not fixed: No feedback loop; verified answers stay frozen at their initial guess of what users would ask.
- owner platform-team
- Source (inferred): Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`WSP-002` Copilot cannot be enabled per workload - the audience decision is all-or-nothing** - _partial_
- Requirement: The rollout plan must account for the fact that enabling Copilot in a capacity for a user or security group grants that group all Copilot workloads and experiences; it cannot be enabled for one experience only.
- Fix: Rewrite the rollout plan around security groups and dedicated capacities.
- If not fixed: Users reach Copilot experiences over unprepared workloads that were never in the pilot scope.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`WSP-003` Staging, development and sandbox workspaces are excluded from AI capacity** - _unknown_
- Requirement: Development, staging and personal sandbox workspaces must not sit on capacity where Copilot is enabled for business users.
- Fix: Move non-production workspaces to a separate capacity or restrict the Copilot security group to production workspace members.
- If not fixed: Users get answers from unfinished models and lose confidence permanently.
- Source (inferred): Established semantic modeling / Copilot tuning practice (not a single Microsoft doc); [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`WSP-006` Semantic model description is populated for discovery** - _unknown_
- Requirement: Each in-scope semantic model must have a populated description in model settings that names the subject areas, key entities and the questions it is meant to answer.
- Fix: Write a description covering tables, measures, relationships and intended audience, using distinct keywords rather than generic phrasing.
- If not fixed: Standalone Copilot routes questions to the wrong model.
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)


### Medium

**`AGT-010` Schema object descriptions are used on the preview runtime where available** - _fail_
- Requirement: Where the preview runtime supports schema object descriptions, they must be applied to abbreviated or generic names, columns with codes, flags, units or category values, date columns tied to a business event, and objects in large schemas.
- Fix: Apply descriptions following the documented priority order.
- If not fixed: Non-semantic-model sources reason from bare column names.
- owner platform-team
- Source (documented): [Best practices for configuring your data agent](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices)

**`DAT-003` Format strings are set on AI-visible measures and columns** - _unknown_
- Requirement: Measures and columns must carry appropriate format strings, since format string is part of the grounding data.
- Fix: Set currency, percentage and precision formats explicitly.
- If not fixed: Percentages presented as raw decimals and currency without denomination.
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MEA-008` Business KPIs are defined in the model** - _fail_
- Requirement: Business-relevant KPIs such as ROI, CAC and LTV should be defined as measures where they are part of the question scope.
- Fix: Implement the KPIs with the official definitions and describe the calculation basis.
- If not fixed: Users ask for a named KPI and receive an approximation the generator assembled.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`MEA-010` DAX comments are not used to convey meaning to Copilot** - _fail_
- Requirement: Semantic context must live in descriptions, not in DAX comments.
- Fix: Move the business meaning into the description; keep comments for maintainers.
- If not fixed: Carefully documented measures that Copilot understands no better than undocumented ones.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MEA-012` Variable-heavy measures are validated for filter and grouping behaviour** - _partial_
- Requirement: Measures making heavy use of DAX variables must be tested, because Copilot may inappropriately filter or group on already-declared variables.
- Fix: Simplify the public-facing measure and push variable complexity into helper measures excluded from the AI schema.
- If not fixed: Subtly wrong filter context in generated queries.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MET-007` Q&A retirement in December 2026 is tracked as a dependency** - _partial_
- Requirement: The roadmap must record that Q&A retires in December 2026 and that a replacement setting will carry instance value indexing forward, with an owner assigned to track the transition.
- Fix: Add it to the platform dependency register and re-check the replacement setting each quarter.
- If not fixed: A dated platform change lands unmanaged on a production AI surface.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`MET-008` Report visuals carry descriptive titles** - _fail_
- Requirement: Visuals on reports within the AI surface must have descriptive titles rather than default or decorative ones.
- Fix: Retitle visuals to name the metric and the grain, for example Revenue by Region, Last 12 Months.
- If not fixed: Weak grounding for visual-level questions and poorer report summaries.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices); [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`MET-010` Refresh timeliness is communicated in metadata** - _partial_
- Requirement: The refresh schedule and data currency must be stated in the semantic model description or AI instructions.
- Fix: Add a line such as: data refreshes nightly at 02:00 UTC; today's transactions are not included.
- If not fixed: Decisions made on stale figures presented without qualification.
- owner platform-team
- Source (documented): [Optimize your semantic model for Copilot in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)

**`OPS-005` Responsible AI guidance is published to users** - _fail_
- Requirement: User-facing guidance must cover validation expectations, non-determinism, the limits of the question scope, and how to report a wrong answer.
- Fix: Publish it at the point of use rather than burying it in a policy document.
- If not fixed: Users with no framework for judging or challenging AI output.
- owner platform-team
- Source (documented): [Copilot in Power BI tutorial: prepare a semantic model for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/tutorial-copilot-power-bi-prepare-model); [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md)

**`SCH-015` Instance-value reindexing cadence is understood and accounted for** - _fail_
- Requirement: The team must document the reindexing behaviour that applies to each model type and set user expectations accordingly.
- Fix: Document it, and for low-traffic but important models schedule a periodic synthetic question to keep the model within the activity window.
- If not fixed: Stale instance values produce filter misses that look like data errors.
- owner platform-team
- Source (documented): [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)

**`SCH-016` DirectQuery indexing constraints are accepted or mitigated** - _partial_
- Requirement: For DirectQuery models, confirm the source supports APPROXIMATEDISTINCTCOUNT and accept that indexing occurs at most once per 24 hours unless the model is republished.
- Fix: Where the source does not support it, consider Import or Direct Lake for the AI-facing model.
- If not fixed: Value filtering effectively unavailable on DirectQuery models against unsupported sources.
- owner platform-team
- Source (documented): [Frequently asked questions about preparing data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-faq)

**`SCH-019` Connection type is supported for Desktop-based Prep for AI authoring** - _fail_
- Requirement: Where Prep for AI is authored in Power BI Desktop, the model must use Import, DirectQuery or local Composite mode.
- Fix: Author Prep for AI in the service for model types Desktop does not support.
- If not fixed: Prep for AI unavailable in Desktop and the team assumes the feature is broken.
- owner platform-team
- Source (documented): [Prepare your data for AI to improve Copilot results (preview)](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)

**`SEC-008` Object-level security interaction with AI grounding is tested** - _fail_
- Requirement: Where OLS is in use, confirm through testing how restricted objects behave in Copilot grounding and in generated queries.
- Fix: Record actual observed behaviour per model and feed it into the security design.
- If not fixed: OLS assumptions that do not hold on the AI path.
- owner platform-team
- Source (inferred): Established semantic modeling / Copilot tuning practice (not a single Microsoft doc)

**`VAL-009` Precision targets are set deliberately per question class** - _partial_
- Requirement: The required precision must be agreed per question class, recognising that higher precision requirements make a response harder to generate at all.
- Fix: Reserve strict precision for financial and regulatory questions; allow exploratory questions to be directional.
- If not fixed: Either dangerous imprecision on regulated numbers or a system that refuses to answer exploratory questions.
- owner platform-team
- Source (documented): [chat-with-your-data-solution-accelerator - best practices](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator/blob/main/docs/best_practices.md)

**`VER-003` Verified answers use no more than three filters** - _fail_
- Requirement: Configure up to three filters per verified answer to keep it flexible for slicing.
- Fix: Where more slicing is needed, create a second verified answer rather than overloading one.
- If not fixed: Configuration rejected or the answer becomes too narrow to fire.
- owner platform-team
- Source (documented): [Semantic model best practices for data agent](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)

**`VER-006` Verified answer authoring prerequisites are met** - _fail_
- Requirement: Authors creating verified answers in the Power BI service must be in a Copilot-enabled workspace, hold authoring permission on the underlying semantic model, be on a report page in edit mode, with the visual selected.
- Fix: Publish the five conditions in the authoring guide as a troubleshooting checklist.
- If not fixed: Authors blocked with no visible reason and the capability goes unused.
- owner platform-team
- Source (documented): [Prepare your data for AI to improve Copilot results (preview)](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)


### Low

**`AGT-008` The underlying LLM cannot be changed - accept and design around it** - _partial_
- Requirement: Design decisions must not assume the ability to substitute the model behind a Fabric data agent.
- Fix: Direct tuning effort at the grounding configuration instead.
- If not fixed: Effort spent on an option that does not exist.
- owner platform-team
- Source (documented): [Fabric data agent creation](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)

**`MEA-011` Newer DAX functions are used cautiously in AI-facing models** - _partial_
- Requirement: Where a model relies on recently introduced DAX functions or syntax, the team must test AI behaviour against those measures specifically.
- Fix: Wrap the newer logic in a stable named measure so the generator references rather than rewrites it.
- If not fixed: Generation errors concentrated in the newest parts of the model.
- owner platform-team
- Source (documented): [Use Copilot with semantic models in Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-semantic-models)

**`SCH-017` Prep for AI changes are given time to propagate before re-testing** - _partial_
- Requirement: Test cycles must allow up to 24 hours for Prep for AI changes to affect Copilot results, typically within an hour, with the longer tail on models that have many attached reports.
- Fix: Build the wait into the evaluation cadence; batch configuration changes rather than tuning one setting at a time.
- If not fixed: Configuration churn and false conclusions about which settings help.
- owner platform-team
- Source (documented): [Prepare your data for AI to improve Copilot results (preview)](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)
