# Changelog

Rule pack versions use `YYYY.MM.N`. The pack version lives in `rules/_meta.json` and is
carried into `AssessmentRules.json` on build.

## 2026.09.1 — 2026-09-10

Initial draft.

- 138 rules across 15 areas: tenant, capacity, workspace, AI data schema, model structure,
  metadata, measures, data types, security, verified answers, AI instructions, data agent
  configuration, performance, response validity, operations.
- 122 rules `documented` against Microsoft Learn; 16 `inferred` and flagged as such.
- 8 blocker rules with a maturity gate.
- 17 hard and soft platform limits encoded with `hard` flags and source citations.
- Three scoring instruments — CLI harness, Excel workbook, HTML console — verified to produce
  identical scores on the same evidence.
- Broad-scan triage path: a 9-rule ordered diagnostic for the "scans everything before
  answering" symptom.

### Open items for the next revision

- Automated evidence collectors for the `api`, `dax`, `tmdl`, `vpax` and `metrics` check methods.
- Re-verify all `documented` limits; several cited features are in preview.
- Track the announced December 2026 Q&A retirement (`MET-007`) and its replacement setting.
